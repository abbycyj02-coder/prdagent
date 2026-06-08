from __future__ import annotations

from backend.agents.schema import field_map


def generate_questions(product_type: str, missing_fields: list[str], max_questions: int = 5) -> list[dict[str, str]]:
    fields = field_map(product_type)
    questions: list[dict[str, str]] = []
    for key in missing_fields[:max_questions]:
        item = fields.get(key)
        if not item:
            continue
        questions.append(
            {
                "field": key,
                "label": item["label"],
                "question": item["question"],
                "placeholder": item["placeholder"],
            }
        )
    return questions

