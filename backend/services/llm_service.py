from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
DEFAULT_MODEL = "gpt-5.4"


def load_env_file() -> None:
    if not ENV_FILE.exists():
        return
    for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file()


def llm_enabled() -> bool:
    if os.getenv("PRD_AGENT_USE_LLM", "1").lower() in {"0", "false", "no"}:
        return False
    return bool(os.getenv("OPENAI_API_KEY"))


def current_model() -> str:
    return os.getenv("OPENAI_MODEL", DEFAULT_MODEL)


def _api_url() -> str:
    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    return f"{base}/chat/completions"


def _redact(value: str) -> str:
    return re.sub(r"sk-[A-Za-z0-9_-]+", "sk-***", value)


def chat_completion(
    messages: list[dict[str, str]],
    response_format: dict[str, Any] | None = None,
    max_completion_tokens: int | None = None,
    timeout: int | None = None,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    payload: dict[str, Any] = {
        "model": current_model(),
        "messages": messages,
    }
    token_budget = max_completion_tokens
    if token_budget is None:
        env_budget = os.getenv("OPENAI_MAX_COMPLETION_TOKENS", "12000").strip()
        token_budget = int(env_budget) if env_budget else 12000
    payload["max_completion_tokens"] = token_budget
    if response_format:
        payload["response_format"] = response_format

    req = urllib.request.Request(
        _api_url(),
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        request_timeout = timeout or int(os.getenv("OPENAI_TIMEOUT", "240"))
        with urllib.request.urlopen(req, timeout=request_timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(_redact(f"OpenAI API error {exc.code}: {detail[:500]}")) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenAI network error: {exc.reason}") from exc

    try:
        return body["choices"][0]["message"]["content"] or ""
    except Exception as exc:
        raise RuntimeError("OpenAI response did not contain message content") from exc


def json_completion(messages: list[dict[str, str]], max_completion_tokens: int = 1600, timeout: int = 90) -> dict[str, Any]:
    text = chat_completion(
        messages,
        response_format={"type": "json_object"},
        max_completion_tokens=max_completion_tokens,
        timeout=timeout,
    )
    return parse_json_object(text)


def parse_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text).strip()
        text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            raise
        return json.loads(match.group(0))
