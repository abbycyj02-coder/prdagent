from __future__ import annotations

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from backend.agents.clarification_agent import generate_questions
from backend.agents.chat_agent import build_assistant_message, extract_answers_from_message, wants_to_generate
from backend.agents.completeness_checker import check_completeness
from backend.agents.prd_generator import generate_prd
from backend.agents.review_agent import review_prd
from backend.agents.router_agent import route_product
from backend.models import SessionState, new_session_id
from backend.services.export_service import export_session
from backend.services.llm_service import current_model, llm_enabled
from backend.store import delete_session, get_session, list_sessions, save_session


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
EXPORT_DIR = ROOT / "exports"
HOST = "127.0.0.1"
PORT = 8787


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict | list) -> None:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _error(handler: BaseHTTPRequestHandler, status: int, message: str) -> None:
    _json_response(handler, status, {"error": message})


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    if length <= 0:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    return json.loads(raw or "{}")


def _refresh_session_status(session: SessionState) -> None:
    result = check_completeness(session.product_type or "software", session.user_input, session.answers)
    session.completeness_score = result["score"]
    session.missing_fields = result["missing_fields"]
    if session.completeness_score >= 70:
        session.questions = []
        session.status = "ready_to_generate" if not session.prd_markdown else session.status
    else:
        session.questions = generate_questions(session.product_type or "software", session.missing_fields)
        session.status = "need_clarification"


class PRDAgentHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        print(f"[server] {self.address_string()} - {fmt % args}")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/health":
            return _json_response(
                self,
                200,
                {
                    "status": "ok",
                    "llm_enabled": llm_enabled(),
                    "model": current_model(),
                },
            )

        if path == "/api/prd/history":
            return _json_response(self, 200, list_sessions())

        if path.startswith("/api/prd/session/"):
            session_id = path.rsplit("/", 1)[-1]
            session = get_session(session_id)
            if not session:
                return _error(self, 404, "session not found")
            return _json_response(self, 200, session.to_dict())

        if path == "/api/prd/export":
            params = parse_qs(parsed.query)
            session_id = (params.get("session_id") or [""])[0]
            export_type = (params.get("type") or ["docx"])[0]
            session = get_session(session_id)
            if not session:
                return _error(self, 404, "session not found")
            try:
                result = export_session(session, export_type)
            except Exception as exc:
                return _error(self, 400, str(exc))
            session.exports.append(result)
            session.status = "exported"
            save_session(session)
            return _json_response(self, 200, result)

        if path.startswith("/exports/"):
            export_name = Path(unquote(path.replace("/exports/", "", 1))).name
            return self._serve_file(EXPORT_DIR / export_name, download=True)

        if path == "/":
            return self._serve_file(PUBLIC_DIR / "index.html")

        return self._serve_file(PUBLIC_DIR / path.lstrip("/"))

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            body = _read_json(self)
        except json.JSONDecodeError:
            return _error(self, 400, "invalid json")

        if path == "/api/prd/create":
            user_input = str(body.get("user_input", "")).strip()
            if len(user_input) < 4:
                return _error(self, 400, "请输入至少 4 个字符的产品想法")
            route = route_product(user_input)
            session = SessionState(
                session_id=new_session_id(),
                user_input=user_input,
                product_type=route.product_type,
                sub_type=route.sub_type,
                confidence=route.confidence,
                route_reasons=route.reasons,
                status="routed",
            )
            _refresh_session_status(session)
            session.chat_messages = [
                {"role": "user", "content": user_input, "created_at": session.created_at},
                {
                    "role": "assistant",
                    "content": build_assistant_message(session, initial=True),
                    "created_at": session.updated_at,
                },
            ]
            save_session(session)
            return _json_response(self, 200, session.to_dict())

        if path == "/api/prd/answer":
            session = get_session(str(body.get("session_id", "")))
            if not session:
                return _error(self, 404, "session not found")
            answers = body.get("answers", {})
            if not isinstance(answers, dict):
                return _error(self, 400, "answers must be an object")
            session.answers.update({str(k): str(v).strip() for k, v in answers.items()})
            if answers:
                session.chat_messages.append(
                    {
                        "role": "user",
                        "content": "\n".join(f"{k}: {v}" for k, v in answers.items()),
                        "created_at": session.updated_at,
                    }
                )
            session.prd_markdown = ""
            session.quality_report = {}
            _refresh_session_status(session)
            session.chat_messages.append(
                {
                    "role": "assistant",
                    "content": build_assistant_message(session, answers),
                    "created_at": session.updated_at,
                }
            )
            save_session(session)
            return _json_response(self, 200, session.to_dict())

        if path == "/api/prd/chat":
            session = get_session(str(body.get("session_id", "")))
            if not session:
                return _error(self, 404, "session not found")
            message = str(body.get("message", "")).strip()
            if len(message) < 1:
                return _error(self, 400, "message is required")

            session.chat_messages.append(
                {"role": "user", "content": message, "created_at": session.updated_at}
            )

            extracted = extract_answers_from_message(session, message)
            if extracted:
                session.answers.update(extracted)
                session.prd_markdown = ""
                session.quality_report = {}

            _refresh_session_status(session)

            generated_now = False
            if wants_to_generate(message):
                session.status = "generating"
                session.prd_markdown = generate_prd(session)
                session.quality_report = review_prd(
                    session.product_type or "software",
                    session.prd_markdown,
                    session.missing_fields,
                )
                session.status = "reviewed"
                assistant_text = (
                    "我已经根据当前对话生成了一份完整详细 PRD，并完成质量评审。"
                    "你可以在右侧预览、编辑、重新评审或导出 Word / PDF。"
                )
                generated_now = True
            else:
                assistant_text = build_assistant_message(session, extracted)

            session.chat_messages.append(
                {"role": "assistant", "content": assistant_text, "created_at": session.updated_at}
            )
            save_session(session)
            payload = session.to_dict()
            payload["generated_now"] = generated_now
            payload["extracted_answers"] = extracted
            return _json_response(self, 200, payload)

        if path == "/api/prd/update-type":
            session = get_session(str(body.get("session_id", "")))
            if not session:
                return _error(self, 404, "session not found")
            product_type = str(body.get("product_type", ""))
            if product_type not in {"software", "hardware", "enterprise"}:
                return _error(self, 400, "invalid product_type")
            session.product_type = product_type  # type: ignore[assignment]
            session.sub_type = str(body.get("sub_type") or product_type)
            session.confidence = 1.0
            session.route_reasons = ["用户手动确认产品类型"]
            session.prd_markdown = ""
            session.quality_report = {}
            _refresh_session_status(session)
            session.chat_messages.append(
                {
                    "role": "assistant",
                    "content": build_assistant_message(session, initial=True),
                    "created_at": session.updated_at,
                }
            )
            save_session(session)
            return _json_response(self, 200, session.to_dict())

        if path == "/api/prd/generate":
            session = get_session(str(body.get("session_id", "")))
            if not session:
                return _error(self, 404, "session not found")
            session.status = "generating"
            session.prd_markdown = generate_prd(session)
            session.quality_report = review_prd(
                session.product_type or "software",
                session.prd_markdown,
                session.missing_fields,
            )
            session.status = "reviewed"
            session.chat_messages.append(
                {
                    "role": "assistant",
                    "content": "我已经生成完整详细 PRD，并完成质量评审。你可以继续补充要求后重新生成，或直接导出 Word / PDF。",
                    "created_at": session.updated_at,
                }
            )
            save_session(session)
            return _json_response(self, 200, session.to_dict())

        if path == "/api/prd/review":
            session = get_session(str(body.get("session_id", "")))
            if not session:
                return _error(self, 404, "session not found")
            markdown = str(body.get("prd_markdown") or session.prd_markdown)
            if not markdown:
                return _error(self, 400, "当前会话没有可评审的 PRD")
            session.prd_markdown = markdown
            session.quality_report = review_prd(
                session.product_type or "software",
                session.prd_markdown,
                session.missing_fields,
            )
            session.status = "reviewed"
            save_session(session)
            return _json_response(self, 200, session.to_dict())

        return _error(self, 404, "not found")

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/prd/session/"):
            session_id = parsed.path.rsplit("/", 1)[-1]
            ok = delete_session(session_id)
            return _json_response(self, 200, {"deleted": ok})
        return _error(self, 404, "not found")

    def _serve_file(self, path: Path, download: bool = False) -> None:
        if not path.exists() or not path.is_file():
            return _error(self, 404, "file not found")
        content = path.read_bytes()
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        if download:
            fallback = f"prd{path.suffix}"
            encoded_name = quote(path.name)
            self.send_header(
                "Content-Disposition",
                f"attachment; filename=\"{fallback}\"; filename*=UTF-8''{encoded_name}",
            )
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), PRDAgentHandler)
    print(f"PRD Agent MVP running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
