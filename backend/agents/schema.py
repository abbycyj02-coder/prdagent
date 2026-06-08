from __future__ import annotations


PRODUCT_SCHEMAS = {
    "software": {
        "name": "软件 / App / SaaS / AI Agent",
        "description": "适用于 Web、App、小程序、SaaS、AI Agent、数据工具、后台系统等。",
        "fields": [
            {
                "key": "target_user",
                "label": "目标用户",
                "question": "这个产品主要给谁用？",
                "placeholder": "例如：产品经理、创业者、业务负责人、研发团队",
                "weight": 15,
            },
            {
                "key": "core_scenario",
                "label": "核心场景",
                "question": "用户会在什么场景下使用这个产品？",
                "placeholder": "例如：接到新需求后，需要快速起草 PRD",
                "weight": 15,
            },
            {
                "key": "core_task",
                "label": "核心任务",
                "question": "用户最核心要完成什么任务？",
                "placeholder": "例如：把一句话想法转成可评审 PRD",
                "weight": 15,
            },
            {
                "key": "output_format",
                "label": "输出格式",
                "question": "最终需要输出什么格式？",
                "placeholder": "例如：Markdown、Word、PDF、结构化 JSON",
                "weight": 10,
            },
            {
                "key": "permission",
                "label": "权限与后台",
                "question": "是否需要登录、权限、后台或付费能力？",
                "placeholder": "例如：MVP 不登录；后续支持团队账号和历史记录",
                "weight": 10,
            },
            {
                "key": "metrics",
                "label": "成功指标",
                "question": "你希望用哪些指标判断产品成功？",
                "placeholder": "例如：生成成功率、导出率、平均生成耗时",
                "weight": 10,
            },
            {
                "key": "exceptions",
                "label": "异常情况",
                "question": "有哪些异常情况必须处理？",
                "placeholder": "例如：输入过短、分类失败、生成失败、导出失败",
                "weight": 15,
            },
            {
                "key": "mvp_scope",
                "label": "MVP 边界",
                "question": "第一版必须做什么，明确不做什么？",
                "placeholder": "例如：做生成闭环，不做多人协作和知识库",
                "weight": 10,
            },
        ],
    },
    "hardware": {
        "name": "智能硬件",
        "description": "适用于 AR 眼镜、AI 玩具、机器人、可穿戴设备、IoT 设备等。",
        "fields": [
            {
                "key": "target_user",
                "label": "目标用户",
                "question": "目标用户是谁，主要使用场景是什么？",
                "placeholder": "例如：商务人士、会议记录用户、户外工作者",
                "weight": 12,
            },
            {
                "key": "usage_scene",
                "label": "物理使用场景",
                "question": "产品会在什么物理环境中使用？",
                "placeholder": "例如：会议室、通勤、户外、工厂、家庭",
                "weight": 12,
            },
            {
                "key": "product_form",
                "label": "产品形态",
                "question": "产品形态是佩戴、手持、固定安装还是桌面使用？",
                "placeholder": "例如：轻量佩戴式 AR 眼镜",
                "weight": 12,
            },
            {
                "key": "hardware_capability",
                "label": "关键硬件能力",
                "question": "最重要的硬件能力是什么？摄像头、麦克风、显示、传感器还是通信？",
                "placeholder": "例如：麦克风阵列、显示模组、摄像头、蓝牙/Wi-Fi",
                "weight": 16,
            },
            {
                "key": "constraints",
                "label": "续航/重量/尺寸/成本",
                "question": "续航、重量、尺寸、成本分别有什么约束？",
                "placeholder": "例如：重量小于 80g，续航 4 小时，BOM 控制在 800 元",
                "weight": 14,
            },
            {
                "key": "app_cloud",
                "label": "App / 云端 / OTA",
                "question": "是否需要配套 App、云端服务或 OTA？",
                "placeholder": "例如：需要手机 App 绑定、云端 AI 处理、固件 OTA",
                "weight": 12,
            },
            {
                "key": "privacy_safety",
                "label": "隐私与安全",
                "question": "是否涉及摄像、录音、定位等敏感能力？",
                "placeholder": "例如：录音需提示灯，用户可关闭麦克风",
                "weight": 10,
            },
            {
                "key": "certification",
                "label": "认证与销售地区",
                "question": "销售地区和认证要求是什么？",
                "placeholder": "例如：中国大陆，需无线电、蓝牙、RoHS 等确认",
                "weight": 12,
            },
        ],
    },
    "enterprise": {
        "name": "政企 / ToB / ToG / 合规",
        "description": "适用于政府、国企、大型企业、金融、医疗、教育等强流程强合规场景。",
        "fields": [
            {
                "key": "organization",
                "label": "组织部门",
                "question": "这个系统服务于哪个组织或部门？",
                "placeholder": "例如：市政务服务局、审批科、监管部门",
                "weight": 12,
            },
            {
                "key": "roles",
                "label": "角色权限",
                "question": "有哪些角色？每个角色能看什么、能做什么？",
                "placeholder": "例如：企业用户、经办人、审核人、审批人、管理员",
                "weight": 16,
            },
            {
                "key": "workflow",
                "label": "业务流程",
                "question": "核心业务流程是什么？是否有审批、退回、补正、驳回？",
                "placeholder": "例如：提交材料 -> 经办审核 -> 领导审批 -> 归档",
                "weight": 18,
            },
            {
                "key": "sensitive_data",
                "label": "敏感数据",
                "question": "是否涉及个人信息、敏感数据或内部数据？",
                "placeholder": "例如：企业证照、联系人手机号、审批材料、操作日志",
                "weight": 12,
            },
            {
                "key": "external_systems",
                "label": "外部系统对接",
                "question": "是否需要对接统一身份、证照库、短信、电子签章、档案或 OA？",
                "placeholder": "例如：统一身份、短信平台、电子证照库、OA",
                "weight": 12,
            },
            {
                "key": "deployment",
                "label": "部署环境",
                "question": "部署在公网、私有化、内网还是政务云？",
                "placeholder": "例如：政务云私有化部署，内网访问",
                "weight": 10,
            },
            {
                "key": "acceptance",
                "label": "验收标准",
                "question": "项目验收看哪些指标和材料？",
                "placeholder": "例如：流程跑通、权限正确、日志可审计、培训材料齐全",
                "weight": 10,
            },
            {
                "key": "policy_basis",
                "label": "政策/制度依据",
                "question": "是否有政策、制度、会议纪要或招标文件作为依据？",
                "placeholder": "例如：内部制度、招标文件、会议纪要、等保要求",
                "weight": 10,
            },
        ],
    },
}


def get_schema(product_type: str) -> dict:
    return PRODUCT_SCHEMAS[product_type]


def field_label(product_type: str, key: str) -> str:
    for item in get_schema(product_type)["fields"]:
        if item["key"] == key:
            return item["label"]
    return key


def field_map(product_type: str) -> dict[str, dict]:
    return {item["key"]: item for item in get_schema(product_type)["fields"]}

