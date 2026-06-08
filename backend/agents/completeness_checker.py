from __future__ import annotations

from backend.agents.schema import field_label, get_schema


EMPTY_VALUES = {"", "不确定", "暂不确定", "跳过", "不知道", "待确认", "无"}


def _is_filled(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip() not in EMPTY_VALUES and len(value.strip()) >= 2


def check_completeness(product_type: str, user_input: str, answers: dict[str, str]) -> dict:
    schema = get_schema(product_type)
    fields = schema["fields"]

    total_weight = sum(item["weight"] for item in fields)
    filled_weight = 0
    missing_fields: list[str] = []
    filled_fields: list[str] = []

    for item in fields:
        key = item["key"]
        if _is_filled(answers.get(key)):
            filled_weight += item["weight"]
            filled_fields.append(key)
        else:
            missing_fields.append(key)

    input_bonus = min(20, max(6, len(user_input.strip()) // 8))
    answer_score = int((filled_weight / total_weight) * 80) if total_weight else 0
    score = min(100, input_bonus + answer_score)

    if score >= 85:
        status_hint = "excellent"
    elif score >= 70:
        status_hint = "ready"
    elif score >= 40:
        status_hint = "draftable"
    else:
        status_hint = "need_clarification"

    return {
        "score": score,
        "missing_fields": missing_fields,
        "missing_labels": [field_label(product_type, item) for item in missing_fields],
        "filled_fields": filled_fields,
        "status_hint": status_hint,
    }

