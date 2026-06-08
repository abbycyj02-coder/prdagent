from __future__ import annotations

from backend.agents.schema import field_label, get_schema
from backend.models import SessionState


def _schema_brief(product_type: str) -> str:
    fields = get_schema(product_type)["fields"]
    return "\n".join(
        f"- {item['key']}（{item['label']}）：{item['question']}" for item in fields
    )


def extract_answers_from_message(session: SessionState, message: str) -> dict[str, str]:
    answers = _heuristic_extract(session, message)
    notes = session.answers.get("_conversation_notes", "").strip()
    answers["_conversation_notes"] = f"{notes}\n{message}".strip() if notes else message.strip()
    return answers


def _sentences(message: str) -> list[str]:
    chunks = []
    for raw in message.replace("；", "。").replace("，", "。").replace("\n", "。").split("。"):
        item = raw.strip()
        if item:
            chunks.append(item)
    return chunks or [message.strip()]


def _pick(message: str, keywords: list[str]) -> str:
    low = message.lower()
    chunks = _sentences(message)
    matched = []
    for chunk in chunks:
        chunk_low = chunk.lower()
        if any(keyword.lower() in chunk_low for keyword in keywords):
            matched.append(chunk)
    if matched:
        return "；".join(matched)
    if any(keyword.lower() in low for keyword in keywords):
        return message.strip()
    return ""


def _heuristic_extract(session: SessionState, message: str) -> dict[str, str]:
    product_type = session.product_type or "software"
    maps = {
        "software": {
            "target_user": ["目标用户", "用户", "hr", "招聘", "负责人", "产品经理", "创业者", "业务"],
            "core_scenario": ["场景", "使用", "筛选", "面试", "起草", "沟通", "流程"],
            "core_task": ["支持", "完成", "核心", "任务", "生成", "评分", "导出", "问答", "录入"],
            "output_format": ["导出", "word", "markdown", "pdf", "报告", "json"],
            "permission": ["权限", "登录", "后台", "多人", "协作", "ats", "集成", "先不做", "不做"],
            "metrics": ["指标", "成功率", "分钟", "耗时", "大于", "小于", "留存", "转化"],
            "exceptions": ["异常", "中断", "超时", "失败", "过短", "错误", "风险"],
            "mvp_scope": ["mvp", "先不做", "第一版", "本期", "范围", "首版"],
        },
        "hardware": {
            "target_user": ["目标用户", "用户", "人群", "客户"],
            "usage_scene": ["场景", "环境", "会议", "户外", "家庭", "工厂"],
            "product_form": ["形态", "佩戴", "手持", "桌面", "安装", "机器人", "眼镜"],
            "hardware_capability": ["摄像头", "麦克风", "传感器", "显示", "通信", "能力"],
            "constraints": ["续航", "重量", "尺寸", "成本", "bom", "价格"],
            "app_cloud": ["app", "云端", "ota", "绑定", "同步"],
            "privacy_safety": ["隐私", "安全", "录音", "摄像", "定位", "提示灯"],
            "certification": ["认证", "销售", "地区", "ce", "fcc", "rohs", "蓝牙"],
        },
        "enterprise": {
            "organization": ["组织", "部门", "政府", "政务", "甲方", "单位"],
            "roles": ["角色", "权限", "经办", "审核", "审批", "管理员", "监管"],
            "workflow": ["流程", "提交", "审核", "审批", "退回", "补正", "驳回", "归档"],
            "sensitive_data": ["数据", "个人信息", "敏感", "材料", "证照", "日志"],
            "external_systems": ["对接", "统一身份", "oa", "短信", "电子签章", "证照", "档案"],
            "deployment": ["部署", "内网", "私有化", "政务云", "公网"],
            "acceptance": ["验收", "指标", "材料", "培训", "测试"],
            "policy_basis": ["政策", "制度", "会议纪要", "招标", "等保", "依据"],
        },
    }

    extracted: dict[str, str] = {}
    for field, keywords in maps.get(product_type, maps["software"]).items():
        value = _pick(message, keywords)
        if value:
            existing = session.answers.get(field, "").strip()
            extracted[field] = f"{existing}；{value}" if existing and value not in existing else value

    if not extracted and session.missing_fields:
        extracted[session.missing_fields[0]] = message.strip()
    return extracted


def build_assistant_message(session: SessionState, extracted: dict[str, str] | None = None, initial: bool = False) -> str:
    product_type = session.product_type or "software"
    extracted = extracted or {}
    next_questions = session.questions[:3]

    recorded = ""
    if extracted:
        items = [
            f"{field_label(product_type, key)}：{value}"
            for key, value in extracted.items()
            if not key.startswith("_")
        ]
        recorded = "我已经记录了：\n" + "\n".join(f"- {item}" for item in items) + "\n\n"

    if session.completeness_score >= 70:
        return (
            f"{recorded}"
            f"现在信息完整度是 {session.completeness_score}/100，已经足够生成一份完整详细 PRD。\n"
            "你可以直接点击右侧“生成 PRD”，也可以继续补充更多偏好，例如目标用户、商业模式、功能边界、页面风格、验收指标。"
            "如果仍有细节不足，我会在 PRD 中明确写“请补充 xxx 信息”，不会替你瞎编。"
        )

    question_lines = "\n".join(
        f"{idx + 1}. {item['question']}" for idx, item in enumerate(next_questions)
    )
    prefix = ""
    if initial:
        prefix = (
            f"我先把它识别为「{session.sub_type or product_type}」，分类置信度约 {round(session.confidence * 100)}%。"
            "接下来我会像产品访谈一样追问少量关键问题，帮你把关键词扩展成可交付研发的完整 PRD。\n\n"
        )

    return (
        f"{prefix}{recorded}"
        f"当前信息完整度是 {session.completeness_score}/100。为了让生成的 PRD 更贴合你的真实需求，先回答这几个问题即可：\n"
        f"{question_lines}\n\n"
        "你可以按编号回答，也可以直接用一段话回答，我会自动理解并更新需求。"
        "如果你现在就生成，缺失细节会在 PRD 中以“请补充 xxx 信息”标出。"
    )


def wants_to_generate(message: str) -> bool:
    text = message.strip().lower()
    triggers = [
        "直接生成",
        "开始生成",
        "生成prd",
        "生成 prd",
        "输出prd",
        "输出 prd",
        "开始写prd",
        "开始写 prd",
        "可以了，生成",
        "可以了 生成",
        "可以了，直接",
        "可以了 直接",
        "generate prd",
    ]
    return any(item in text for item in triggers)
