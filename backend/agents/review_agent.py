from __future__ import annotations

from backend.agents.schema import field_label
from backend.services.llm_service import json_completion, llm_enabled


AMBIGUOUS_TERMS = [
    "提升体验",
    "提高效率",
    "更好用",
    "智能化",
    "自动化",
    "高性能",
    "稳定可靠",
    "简单易用",
    "快速",
]


def _rule_review_prd(product_type: str, prd_markdown: str, missing_fields: list[str]) -> dict:
    ambiguous = [term for term in AMBIGUOUS_TERMS if term in prd_markdown]
    pending_count = prd_markdown.count("待确认") + prd_markdown.count("请补充")

    dimension_scores = {
        "完整性": max(0, 100 - len(missing_fields) * 8 - pending_count * 3),
        "清晰度": max(0, 92 - len(ambiguous) * 6),
        "可开发性": 86 if "验收标准" in prd_markdown and "异常" in prd_markdown else 72,
        "可测试性": 88 if "验收标准" in prd_markdown else 68,
        "类型适配": 90,
        "风险覆盖": 86 if "风险" in prd_markdown else 70,
    }

    quality_score = int(sum(dimension_scores.values()) / len(dimension_scores))
    quality_score = max(0, min(100, quality_score))

    missing_labels = [field_label(product_type, field) for field in missing_fields]
    suggestions = []
    if missing_labels:
        suggestions.append(f"补充缺失信息：{', '.join(missing_labels[:6])}")
    if ambiguous:
        suggestions.append("把模糊描述替换为可验证指标，例如成功率、耗时、错误率、导出率")
    if pending_count:
        suggestions.append("将文档中的“请补充/待确认”逐项转成明确结论或人工确认项")
    suggestions.extend(
        [
            "为 P0 功能补充输入、处理逻辑、输出和验收标准",
            "补充异常流程和失败提示，减少研发后期返工",
            "生成后建议由产品、研发、测试各评审一次",
        ]
    )

    risks = [
        {"level": "高", "name": "需求信息不足", "mitigation": "生成前强制追问关键字段，低于 40 分不建议生成正式 PRD"},
        {"level": "中", "name": "模型自由发挥", "mitigation": "通过固定 Schema、模板和评审规则控制输出范围"},
    ]
    if product_type == "enterprise":
        risks.append(
            {
                "level": "高",
                "name": "合规误用",
                "mitigation": "政企类内容必须由法务、安全负责人和甲方主管部门最终确认",
            }
        )

    return {
        "quality_score": quality_score,
        "dimension_scores": dimension_scores,
        "missing_items": missing_labels,
        "ambiguous_terms": ambiguous,
        "pending_count": pending_count,
        "risks": risks,
        "suggestions": suggestions[:6],
    }


def _llm_review_prd(product_type: str, prd_markdown: str, missing_fields: list[str]) -> dict:
    data = json_completion(
        [
            {
                "role": "system",
                "content": (
                    "你是严格的 PRD 质量评审 Agent。只输出 JSON。"
                    "必须包含 quality_score、dimension_scores、missing_items、ambiguous_terms、pending_count、risks、suggestions。"
                    "dimension_scores 必须包含：完整性、清晰度、可开发性、可测试性、类型适配、风险覆盖。"
                    "PRD 中出现“请补充 xxx 信息”是合理的缺口提示，不要当作幻觉；但要把它计入 pending_count 和 missing_items。"
                    "risks 是数组，每项包含 level、name、mitigation。不要只夸文档。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"产品类型：{product_type}\n"
                    f"已知缺失字段：{', '.join(missing_fields) or '无'}\n\n"
                    f"PRD：\n{prd_markdown[:18000]}"
                ),
            },
        ],
        max_completion_tokens=3000,
        timeout=120,
    )
    rule = _rule_review_prd(product_type, prd_markdown, missing_fields)
    dimension_scores = data.get("dimension_scores") or rule["dimension_scores"]
    if not isinstance(dimension_scores, dict):
        dimension_scores = rule["dimension_scores"]
    quality_score = int(data.get("quality_score") or rule["quality_score"])
    return {
        "quality_score": max(0, min(100, quality_score)),
        "dimension_scores": dimension_scores,
        "missing_items": data.get("missing_items") or rule["missing_items"],
        "ambiguous_terms": data.get("ambiguous_terms") or rule["ambiguous_terms"],
        "pending_count": int(data.get("pending_count") or rule["pending_count"]),
        "risks": data.get("risks") or rule["risks"],
        "suggestions": data.get("suggestions") or rule["suggestions"],
    }


def review_prd(product_type: str, prd_markdown: str, missing_fields: list[str]) -> dict:
    if llm_enabled():
        try:
            return _llm_review_prd(product_type, prd_markdown, missing_fields)
        except Exception:
            result = _rule_review_prd(product_type, prd_markdown, missing_fields)
            return result
    return _rule_review_prd(product_type, prd_markdown, missing_fields)
