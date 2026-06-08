from __future__ import annotations

from backend.models import RouteResult
from backend.services.llm_service import json_completion, llm_enabled


HARDWARE_KEYWORDS = {
    "ar": 3,
    "眼镜": 3,
    "硬件": 3,
    "机器人": 3,
    "设备": 2,
    "传感器": 3,
    "摄像头": 2,
    "麦克风": 2,
    "电池": 2,
    "续航": 2,
    "量产": 3,
    "bom": 3,
    "固件": 2,
    "ota": 2,
    "可穿戴": 3,
    "iot": 3,
}

ENTERPRISE_KEYWORDS = {
    "政府": 3,
    "政务": 3,
    "政企": 3,
    "审批": 3,
    "监管": 3,
    "国企": 3,
    "甲方": 2,
    "权限": 2,
    "审计": 3,
    "等保": 3,
    "合规": 2,
    "流程": 1,
    "oa": 2,
    "内网": 2,
    "政务云": 3,
}

SOFTWARE_KEYWORDS = {
    "app": 2,
    "小程序": 2,
    "web": 2,
    "网站": 2,
    "saas": 3,
    "agent": 3,
    "ai": 2,
    "系统": 1,
    "平台": 1,
    "后台": 2,
    "crm": 3,
    "数据分析": 2,
}


def _score(text: str, keywords: dict[str, int]) -> tuple[int, list[str]]:
    hits: list[str] = []
    score = 0
    low = text.lower()
    for keyword, weight in keywords.items():
        if keyword.lower() in low:
            score += weight
            hits.append(keyword)
    return score, hits


def _sub_type(text: str, product_type: str) -> str:
    low = text.lower()
    if product_type == "software":
        if "agent" in low:
            return "AI Agent"
        if "saas" in low:
            return "SaaS"
        if "小程序" in text:
            return "小程序"
        if "后台" in text:
            return "运营后台"
        return "软件产品"
    if product_type == "hardware":
        if "ar" in low or "眼镜" in text:
            return "AR 眼镜"
        if "机器人" in text:
            return "机器人"
        if "玩具" in text:
            return "AI 玩具"
        return "智能硬件"
    if "审批" in text:
        return "审批系统"
    if "监管" in text:
        return "监管平台"
    return "政企系统"


def _route_product_rules(user_input: str) -> RouteResult:
    text = user_input.strip()
    hardware_score, hardware_hits = _score(text, HARDWARE_KEYWORDS)
    enterprise_score, enterprise_hits = _score(text, ENTERPRISE_KEYWORDS)
    software_score, software_hits = _score(text, SOFTWARE_KEYWORDS)

    scores = {
        "software": software_score,
        "hardware": hardware_score,
        "enterprise": enterprise_score,
    }
    hits = {
        "software": software_hits,
        "hardware": hardware_hits,
        "enterprise": enterprise_hits,
    }

    product_type = max(scores, key=scores.get)
    top_score = scores[product_type]
    second_score = sorted(scores.values(), reverse=True)[1]

    if top_score == 0:
        product_type = "software"
        confidence = 0.42
        reasons = ["未命中强类型关键词，默认按软件类需求处理，建议用户确认类型"]
    else:
        margin = max(0, top_score - second_score)
        confidence = min(0.96, 0.52 + top_score * 0.06 + margin * 0.05)
        reasons = [f"命中关键词：{', '.join(hits[product_type])}"]
        if margin <= 1 and second_score > 0:
            reasons.append("存在跨类型信号，建议在页面中确认产品类型")

    return RouteResult(
        product_type=product_type,  # type: ignore[arg-type]
        sub_type=_sub_type(text, product_type),
        confidence=round(confidence, 2),
        reasons=reasons,
    )


def _route_product_llm(user_input: str) -> RouteResult:
    data = json_completion(
        [
            {
                "role": "system",
                "content": (
                    "你是 PRD 生成 Agent 的产品类型识别器。"
                    "只输出 JSON，字段为 product_type、sub_type、confidence、reasons。"
                    "product_type 只能是 software、hardware、enterprise。"
                    "confidence 是 0 到 1 的数字。不要编造用户没有表达的事实。"
                ),
            },
            {"role": "user", "content": f"用户输入：{user_input}"},
        ]
    )
    product_type = str(data.get("product_type", "software")).strip()
    if product_type not in {"software", "hardware", "enterprise"}:
        product_type = "software"
    confidence = float(data.get("confidence", 0.7))
    confidence = max(0.0, min(1.0, confidence))
    reasons = data.get("reasons") or ["LLM 分类结果"]
    if isinstance(reasons, str):
        reasons = [reasons]
    reasons = [f"LLM：{item}" for item in reasons[:4]]
    return RouteResult(
        product_type=product_type,  # type: ignore[arg-type]
        sub_type=str(data.get("sub_type") or _sub_type(user_input, product_type)),
        confidence=round(confidence, 2),
        reasons=reasons,
    )


def route_product(user_input: str) -> RouteResult:
    if llm_enabled():
        try:
            return _route_product_llm(user_input)
        except Exception as exc:
            fallback = _route_product_rules(user_input)
            fallback.reasons.append(f"LLM 分类失败，已回退规则分类：{exc}")
            return fallback
    return _route_product_rules(user_input)
