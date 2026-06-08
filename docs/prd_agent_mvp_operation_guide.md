# PRD 生成 Agent MVP 操作步骤与需求文档评审

## 1. MVP 验证目标

本 MVP 的目标不是一次性做完整企业级平台，而是在 2-3 周内验证一个核心假设：

用户输入一句模糊产品想法后，系统能识别产品类型，提出关键追问，并生成一份结构完整、可评审、可导出的 PRD 初稿。

成功标准：

- 用户可以在 10 分钟内从一句想法得到一份 PRD 草稿。
- 系统能稳定区分软件、智能硬件、政企合规三类需求。
- 信息不足时，系统不会直接“硬编”，而是先追问 3-5 个关键问题。
- 生成后的 PRD 有完整度评分、质量评审、缺失项和优化建议。
- 支持 Markdown 导出；Word 导出作为 MVP 增强项。

## 2. MVP 范围

### 2.1 必做范围

- 自然语言输入入口。
- 产品类型识别：software / hardware / enterprise。
- 每类产品一套必填字段 Schema。
- 完整度评分：0-100 分。
- 澄清问题生成：每轮 3-5 个问题。
- 三类 PRD Markdown 模板生成。
- 质量评审：评分、缺失项、模糊词、风险、优化建议。
- 会话状态保存。
- Markdown 导出。

### 2.2 暂不做范围

- 多人协作、团队空间、企业权限。
- 知识库 RAG、行业法规实时检索。
- 飞书、Notion、Jira 等第三方集成。
- 复杂模板编辑器。
- PDF 精排导出。
- 复杂用户登录系统。

## 3. 建议 MVP 技术方案

### 3.1 技术栈

- 前端：Next.js 或 React。
- 后端：FastAPI。
- Agent 编排：自定义状态机 Workflow。
- 数据库：SQLite，后续可替换为 Supabase/PostgreSQL。
- LLM：通过后端统一封装调用，不在前端暴露 API Key。
- 导出：Markdown 优先；Word 可用 python-docx 或 markdown-to-docx 方案。

### 3.2 MVP 目录结构

```text
backend/
  main.py
  agents/
    router_agent.py
    completeness_checker.py
    clarification_agent.py
    prd_generator.py
    review_agent.py
  schemas/
    prd_schema.py
  services/
    llm_service.py
    export_service.py
  state/
    session_store.py
  templates/
    software_prd.md
    hardware_prd.md
    enterprise_prd.md
frontend/
  src/
    pages/
      index.tsx
      workspace/[session_id].tsx
    components/
      InputPanel.tsx
      QuestionPanel.tsx
      RequirementCard.tsx
      PrdPreview.tsx
      ReviewPanel.tsx
docs/
  prd_agent_mvp_operation_guide.md
```

## 4. MVP 工作流

### 4.1 状态流转

```text
created
  -> routed
  -> need_clarification
  -> ready_to_generate
  -> generated
  -> reviewed
  -> exported
```

### 4.2 处理步骤

1. 用户输入一句产品想法。
2. 后端创建 session，保存原始输入。
3. Router Agent 判断产品类型、子类型和置信度。
4. Schema Selector 加载对应类型的必填字段。
5. Completeness Checker 计算完整度，识别缺失字段。
6. 如果完整度低于阈值，Clarification Agent 生成 3-5 个追问。
7. 用户回答问题，系统更新 session。
8. 完整度达到 70 分后允许生成 PRD。
9. Specialized PRD Agent 按模板生成 Markdown PRD。
10. Review Agent 输出质量报告。
11. 用户复制、下载 Markdown，或继续补充后重新生成。

## 5. 第一版页面操作步骤

### 5.1 首页输入

页面元素：

- 大文本输入框。
- 三个快捷入口：软件 / 智能硬件 / 政企合规。
- 示例输入。
- 敏感信息提示。

用户操作：

1. 输入产品想法，例如“我想做一个能帮产品经理生成 PRD 的 AI Agent”。
2. 点击“开始生成”。
3. 前端调用 `POST /api/prd/create`。

后端返回：

- `session_id`
- `product_type`
- `sub_type`
- `confidence`
- `questions`
- `completeness_score`

### 5.2 需求理解页

页面元素：

- 产品类型识别结果。
- 分类置信度。
- 推荐模板。
- 当前缺失字段。
- “确认类型”和“修改类型”入口。

用户操作：

1. 查看系统识别是否正确。
2. 如果识别错误，手动切换类型。
3. 确认后进入追问页。

### 5.3 多轮问询页

页面元素：

- 3-5 个问题卡片。
- 每题一个回答输入框。
- “不确定 / 跳过”选项。
- 完整度进度条。

用户操作：

1. 回答系统问题。
2. 点击提交。
3. 前端调用 `POST /api/prd/answer`。
4. 如果完整度仍不足，系统继续追问。
5. 如果完整度达到 70 分，进入生成页。

### 5.4 PRD 工作台

页面元素：

- 左侧：对话和追问记录。
- 中间：结构化需求卡片。
- 右侧：PRD Markdown 预览。
- 操作按钮：生成、重新生成、复制、导出。

用户操作：

1. 点击“生成 PRD”。
2. 前端调用 `POST /api/prd/generate`。
3. 等待生成结果。
4. 查看 PRD 预览和质量评分。

### 5.5 质量评审页

页面元素：

- 完整度评分。
- 可开发性评分。
- 风险覆盖评分。
- 缺失项列表。
- 模糊表达列表。
- 优化建议。

用户操作：

1. 根据缺失项补充信息。
2. 可选择重新生成或只重写某个章节。
3. 满意后导出。

### 5.6 导出

MVP 导出优先级：

1. 复制 Markdown。
2. 下载 Markdown 文件。
3. 下载 Word 文件。

## 6. 后端 API 操作步骤

### 6.1 创建会话

接口：`POST /api/prd/create`

请求：

```json
{
  "user_input": "我想做一个能帮产品经理生成 PRD 的 AI Agent",
  "language": "zh-CN"
}
```

响应：

```json
{
  "session_id": "prd_001",
  "product_type": "software",
  "sub_type": "AI Agent",
  "confidence": 0.92,
  "completeness_score": 42,
  "questions": [
    "这个产品主要给谁用？",
    "用户完成的核心任务是什么？",
    "最终需要输出什么格式？",
    "是否需要登录、权限、后台或付费？"
  ],
  "status": "need_clarification"
}
```

### 6.2 提交追问答案

接口：`POST /api/prd/answer`

请求：

```json
{
  "session_id": "prd_001",
  "answers": {
    "target_user": "产品经理、创业者、业务负责人",
    "core_task": "把自然语言产品想法生成结构化 PRD",
    "output_format": "Markdown 和 Word",
    "permission": "MVP 阶段不做复杂权限"
  }
}
```

响应：

```json
{
  "completeness_score": 76,
  "missing_fields": ["数据埋点", "异常流程", "验收标准"],
  "next_questions": [],
  "status": "ready_to_generate"
}
```

### 6.3 生成 PRD

接口：`POST /api/prd/generate`

请求：

```json
{
  "session_id": "prd_001"
}
```

响应：

```json
{
  "prd_markdown": "# PRD 标题...",
  "quality_score": 82,
  "review_comments": {
    "missing_items": ["权限矩阵较弱", "导出失败处理不够具体"],
    "ambiguous_terms": ["提升效率"],
    "suggestions": ["补充 P0 功能验收标准"]
  },
  "status": "reviewed"
}
```

## 7. Prompt 配置操作步骤

### 7.1 Prompt 文件拆分

建议把 Prompt 独立放到配置目录：

```text
prompts/
  router.zh.md
  completeness.zh.md
  clarification.zh.md
  software_prd.zh.md
  hardware_prd.zh.md
  enterprise_prd.zh.md
  review.zh.md
```

### 7.2 输出格式约束

Router、完整度评分、评审报告必须输出 JSON。PRD 生成可以输出 Markdown。

JSON 输出要用 Pydantic 校验，不符合结构时进行一次自动修复；仍失败则返回错误提示，不进入下一节点。

## 8. MVP 测试用例

### 8.1 软件类测试

输入：

```text
我想做一个 AI Agent，帮产品经理把一句话想法生成 PRD。
```

期望：

- 分类为 `software`。
- 子类型为 `AI Agent`。
- 追问目标用户、核心任务、输出格式、权限、指标。
- 生成 PRD 包含页面、流程、功能、埋点、验收标准。

### 8.2 智能硬件测试

输入：

```text
我想做一款 AR 眼镜，可以帮用户实时翻译和记录会议。
```

期望：

- 分类为 `hardware`。
- 追问目标用户、佩戴场景、摄像头/麦克风/显示、续航、重量、认证。
- 生成 PRD 包含工业设计、硬件规格、App/云端协同、隐私、量产阶段。

### 8.3 政企类测试

输入：

```text
我想做一个政府审批系统，支持企业提交材料、工作人员审核、领导审批。
```

期望：

- 分类为 `enterprise`。
- 追问组织部门、角色、审批流程、接口、部署、安全、验收。
- 生成 PRD 包含角色权限矩阵、流程节点、数据字典、接口对接、安全审计、部署运维。

### 8.4 低信息输入测试

输入：

```text
帮我做一个系统。
```

期望：

- 置信度低。
- 不直接生成 PRD。
- 要求用户确认产品类型并补充场景。

## 9. MVP 验收清单

- 输入一句产品想法后，系统能创建 session。
- 三类产品识别准确率在内部测试集中达到 85% 以上。
- 每类产品至少能生成 3-5 个高价值追问。
- 完整度低于 40 分时不生成 PRD。
- 完整度达到 70 分后可以生成 PRD。
- 生成内容覆盖对应类型的核心模块。
- 评审结果包含评分、缺失项、模糊词、风险和建议。
- Markdown 可复制、可下载。
- LLM 调用失败时不丢失用户输入。
- 后端日志不记录完整敏感输入。

## 10. 两到三周执行计划

### 第 1 周：后端闭环

- Day 1：搭建 FastAPI、session 数据结构、SQLite。
- Day 2：实现 Router Agent 和三类 Schema。
- Day 3：实现完整度评分和缺失字段识别。
- Day 4：实现澄清问题生成。
- Day 5：实现三类 PRD Markdown 模板生成。

交付物：

- 后端接口可跑通。
- Postman 或 curl 可完成创建、追问、生成。

### 第 2 周：前端工作台和评审

- Day 6：搭建前端输入页和需求理解页。
- Day 7：实现多轮问询页。
- Day 8：实现 PRD 工作台和 Markdown 预览。
- Day 9：实现 Review Agent 和质量评审页。
- Day 10：实现复制和 Markdown 导出。

交付物：

- 可演示 Web Demo。
- 三类测试输入均能跑通。

### 第 3 周：打磨和演示

- Day 11：补充 Word 导出。
- Day 12：优化 Prompt 和模板。
- Day 13：补充错误处理、重试、日志。
- Day 14：用 20 条测试样例做质量评估。
- Day 15：准备演示脚本和复盘报告。

交付物：

- MVP 演示版本。
- 测试样例和评分记录。
- 下一阶段需求列表。

## 11. 原需求文档的优点

- 核心闭环定义清楚：输入、分类、追问、生成、评审、导出。
- 三类 PRD 的差异写得比较充分，特别是硬件和政企模板不是简单套软件模板。
- 对 Agent 架构的判断合理：MVP 使用状态机比自由多 Agent 更稳定。
- 已经包含接口、状态、目录、Prompt 管理、验收标准和风险。
- 对政企合规有边界意识，明确不替代法务或安全测评。

## 12. 原需求文档的主要不足

### 12.1 MVP 仍然偏大

文档把“三类 PRD 生成、质量评审、Word 导出、历史保存”都放入 P0，2-3 周内可以做演示版，但如果要求稳定产品体验，范围仍偏大。

建议：

- 第一轮只把 Markdown 导出作为 P0。
- Word 导出作为增强项。
- 历史记录先做本地 session 列表，不做复杂管理。

### 12.2 缺少评分公式

文档有评分维度和权重，但缺少字段级评分规则。例如目标用户缺失扣几分、异常流程缺失扣几分、用户回答“不确定”如何计分。

建议：

- 为三类 PRD 分别建立字段权重表。
- 明确必填字段、推荐字段、可选字段。
- 评分结果给出证据来源，避免模型自由打分。

### 12.3 缺少结构化 Schema 明细

文档提到 session 和模板字段，但没有给出三类产品的完整结构化字段定义。

建议：

- 为 software、hardware、enterprise 分别定义 Pydantic Schema。
- 每个字段标注：字段名、类型、是否必填、追问优先级、示例、用于哪个 PRD 章节。

### 12.4 缺少 Prompt 输入输出样例

文档说明了 Prompt 类型，但没有给出少量高质量示例。

建议：

- 增加 Router Prompt 示例。
- 增加 Clarification Prompt 示例。
- 增加 Review Prompt JSON 示例。
- 增加每类 PRD 的生成片段示例。

### 12.5 缺少模型失败和兜底策略

LLM 可能出现 JSON 格式错误、分类不稳定、生成过长、模板漏项、幻觉式补充等问题，文档提到风险但没有落到工程处理。

建议：

- 加 JSON Schema 校验和自动修复。
- 加最大重试次数。
- 对置信度低的分类强制人工确认。
- 对关键字段禁止模型自行编造，必须标注“待确认”。

### 12.6 缺少评测数据集

要验证 Agent 是否有效，需要固定测试集。现在文档有测试方向，但缺少样例库和评估标准。

建议：

- 准备 20 条内部测试输入：软件 8 条、硬件 6 条、政企 6 条。
- 每条标注期望类型、必问问题、必出章节。
- 每次 Prompt 修改后跑一次回归。

### 12.7 缺少成本和时延预算

文档写了生成建议 30-60 秒，但没有拆解每一步调用模型的次数、token 成本、重试成本。

建议：

- MVP 控制在 3-5 次模型调用内。
- Router 和完整度评分可合并为一次调用。
- 评审可以在生成后异步执行。
- 记录每次调用耗时、输入 token、输出 token、失败原因。

### 12.8 缺少导出格式规范

Word 导出被列为 P0，但没有定义 Word 样式规范，如标题层级、表格宽度、页眉页脚、版本记录、评审报告位置。

建议：

- 先固定 Markdown 结构。
- Word 导出只负责把 Markdown 转成稳定样式。
- 为 Word 输出定义样式模板，而不是让模型直接写 Word。

### 12.9 缺少用户修改闭环

文档提到了重写章节，但 MVP 操作流里还不够明确：用户对生成内容不满意时，是补充信息、重写章节，还是修改结构化字段。

建议：

- MVP 先支持“补充一段要求后重新生成”。
- v0.2 再支持单章节重写。
- 结构化需求卡片允许用户编辑关键字段。

### 12.10 缺少产品质量分层

不同用户对 PRD 深度要求不同：创业者可能需要轻量版，政企交付需要重文档。文档还没有明确轻量/标准/详细三种输出深度。

建议：

- 增加输出深度参数：lite / standard / detailed。
- MVP 默认 standard。
- 政企类默认 detailed。

## 13. 建议的最小可验证版本

如果想最快验证效果，建议先做这个最小版本：

- 只做一个 Web 输入页和一个结果页。
- 后端保留完整状态机，但前端先不做复杂工作台。
- 三类模板都支持，但每类只保留核心 8-10 个章节。
- 每次最多一轮追问。
- 生成 Markdown PRD。
- 自动附带质量评审报告。

这样可以在较短时间内验证最关键的问题：

- 用户是否愿意通过追问补充需求。
- 三类模板是否真的比通用 PRD 更有价值。
- 生成的 PRD 是否能帮助研发、设计、测试理解需求。
- 质量评审是否能显著提高用户对文档的信任。

## 14. 下一步建议

建议先按以下顺序推进：

1. 把三类 PRD Schema 定义清楚。
2. 写 20 条测试输入作为评测集。
3. 先实现后端状态机和接口。
4. 再做一个极简前端 Demo。
5. 用测试集评估生成质量。
6. 根据评分结果优化 Prompt 和模板。
7. 最后再做 Word 导出和界面打磨。
