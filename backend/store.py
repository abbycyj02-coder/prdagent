from __future__ import annotations

import json
from pathlib import Path
from threading import Lock

from backend.models import SessionState


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
STORE_FILE = DATA_DIR / "sessions.json"

_lock = Lock()


def _read_raw() -> dict:
    if not STORE_FILE.exists():
        return {}
    try:
        return json.loads(STORE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _write_raw(data: dict) -> None:
    STORE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def save_session(session: SessionState) -> SessionState:
    with _lock:
        data = _read_raw()
        session.touch()
        data[session.session_id] = session.to_dict()
        _write_raw(data)
    return session


def get_session(session_id: str) -> SessionState | None:
    with _lock:
        data = _read_raw()
    item = data.get(session_id)
    if not item:
        return None
    return SessionState.from_dict(item)


def list_sessions() -> list[dict]:
    with _lock:
        data = _read_raw()
    sessions = list(data.values())
    sessions.sort(key=lambda item: item.get("updated_at", ""), reverse=True)
    return sessions


def delete_session(session_id: str) -> bool:
    with _lock:
        data = _read_raw()
        existed = session_id in data
        if existed:
            del data[session_id]
            _write_raw(data)
    return existed

