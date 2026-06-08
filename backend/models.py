from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4


ProductType = Literal["software", "hardware", "enterprise"]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def new_session_id() -> str:
    return f"prd_{uuid4().hex[:8]}"


@dataclass
class RouteResult:
    product_type: ProductType
    sub_type: str
    confidence: float
    reasons: list[str] = field(default_factory=list)


@dataclass
class Question:
    field: str
    label: str
    question: str
    placeholder: str = ""


@dataclass
class SessionState:
    session_id: str
    user_input: str
    product_type: ProductType | None = None
    sub_type: str = ""
    confidence: float = 0.0
    route_reasons: list[str] = field(default_factory=list)
    answers: dict[str, str] = field(default_factory=dict)
    missing_fields: list[str] = field(default_factory=list)
    completeness_score: int = 0
    questions: list[dict[str, str]] = field(default_factory=list)
    chat_messages: list[dict[str, str]] = field(default_factory=list)
    prd_markdown: str = ""
    quality_report: dict[str, Any] = field(default_factory=dict)
    exports: list[dict[str, str]] = field(default_factory=list)
    status: str = "created"
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)

    def touch(self) -> None:
        self.updated_at = now_iso()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionState":
        return cls(**data)
