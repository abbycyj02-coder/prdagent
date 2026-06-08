# PRD Agent MVP
PRD Agent是一个面向产品经理的本地可运行AI Agent MVP。用户只需要输入一句产品想法或关键词，系统会自动识别产品类型、追问缺失信息、检查需求完整度，并生成结构化中文 PRD 文档。最终结果支持在线预览、质量评审、编辑以及Word /PDF导出。
该项目的核心目标是验证：AI是否可以辅助产品经理完成从“模糊需求”到“可评审 PRD 初稿”的工作流。

## Core Features / 核心能力

### 1. 需求理解
- 支持输入一句产品想法或关键词，自动识别产品类型。
- 当前支持三类 PRD 场景：
  - 软件产品
  - 智能硬件产品
  - 政企 / ToB / 合规类系统
- 支持手动修改产品类型和子类型，避免自动分类错误影响后续生成。

### 2. 多 Agent 工作流
系统将产品经理写PRD的过程拆解为多个模块：
```text
User Input
  -> Router Agent
  -> Schema / Completeness Checker
  -> Clarification Agent
  -> Chat Extractor
  -> PRD Generator
  -> Review Agent
  -> Export Service
```
每个模块负责一个独立任务，降低单次 LLM 生成带来的不稳定性。

### 3. 追问与完整度检查

- 当需求信息不足时，系统会生成少量关键追问。
- 用户可以像和ChatGPT对话一样自然语言补充需求。
- 系统会将用户回答沉淀为结构化字段。
- 对未知信息不会直接编造，而是在文档中标记“请补充 xxx 信息”。

### 4. PRD 生成
生成内容按照标准 PRD 主线组织，包括：
- 产品背景
- 目标用户
- 使用场景
- 用户痛点
- 产品目标
- MVP 范围
- 功能模块
- 用户流程
- 验收标准
- 风险与待确认问题

### 5. 质量评审与导出
- 支持从完整性、清晰度、可开发性、可测试性、风险覆盖等维度进行 PRD 质量评审。
- 支持导出 Word 和 PDF。
- Word 导出采用标准化字体设置：中文宋体，英文 Calibri，字号小五。
- 本地保存历史会话，方便继续补充、重新生成和导出。

## 项目亮点
- 设计了从需求识别、信息补全、PRD 生成到质量评审的完整 Agent 工作流。
- 使用 Schema 控制追问和完整度检查，避免完全依赖模型自由发挥。
- 通过产品类型路由，让不同产品方向使用不同 PRD 结构。
- 在信息不足时显式标记待补充内容，减少 LLM 幻觉。
- 实现 Word / PDF 导出，使生成结果从聊天文本变成可交付文档。
- LLM 调用失败时保留本地规则和模板回退能力，保证 MVP 可运行。

## 技术栈
- Backend: Python
- Frontend: HTML, CSS, JavaScript
- LLM: OpenAI API
- Storage: Local JSON session storage
- Export: Word / PDF export service
- Architecture: Multi-agent workflow + Schema-based requirement checking

## 运行方式

### 1. Clone the repository

```bash
git clone https://github.com/abbycyj02-coder/prdagent.git
cd prdagent
```

### 2. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env`:

```text
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=your-model-name
OPENAI_TIMEOUT=240
OPENAI_MAX_COMPLETION_TOKENS=12000
PRD_AGENT_USE_LLM=1
```

> Do not commit your real API key to GitHub. The `.env` file is ignored by `.gitignore`.

### 3. Start the service

```bash
./run.sh
```

Or run directly:

```bash
python3 -m backend.server
```

### 4. Open the web app

```text
http://127.0.0.1:8787
```

---

## 使用步骤

1. 输入一个产品想法，例如：“做一个数字人生成平台”。
2. 点击“开始分析”。
3. 系统会自动识别产品类型和产品子类型。
4. 如果系统识别不准确，可以手动调整产品类型。
5. 根据系统生成的追问，用自然语言补充需求信息。
6. 点击“生成 PRD”，也可以直接输入“可以了，生成 PRD”。
7. 在右侧预览并编辑生成的 PRD 内容。
8. 点击“重新评审”，更新 PRD 的质量评分。
9. 将最终文档导出为 Word 或 PDF。

## Code Structure / 代码结构

```text
backend/
  server.py                         # Local HTTP API and static file service
  models.py                         # Session data models
  store.py                          # Local JSON persistence
  agents/
    router_agent.py                 # Product type routing
    schema.py                       # PRD field schemas
    completeness_checker.py         # Completeness scoring
    clarification_agent.py          # Clarification question generation
    chat_agent.py                   # Chat extraction and generation intent detection
    prd_generator.py                # PRD generation
    review_agent.py                 # PRD quality review
  services/
    llm_service.py                  # OpenAI API wrapper
    export_service.py               # Word / PDF export
public/
  index.html                        # Web workspace
  app.js                            # Frontend interaction logic
  style.css                         # Frontend styles
templates/                          # Local fallback templates
prompts/                            # Prompt drafts
scripts/                            # Helper scripts
docs/
  prd_agent_mvp_operation_guide.md  # MVP operation guide
```

---

## API Overview / API 概览

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Service health check |
| `/api/prd/create` | POST | Create a PRD session and classify product type |
| `/api/prd/chat` | POST | Add requirements through conversation or trigger generation |
| `/api/prd/answer` | POST | Submit structured clarification answers |
| `/api/prd/update-type` | POST | Manually update product type |
| `/api/prd/generate` | POST | Generate PRD and run quality review |
| `/api/prd/review` | POST | Re-review an edited PRD |
| `/api/prd/export` | GET | Export PRD as Word or PDF |
| `/api/prd/history` | GET | View session history |
| `/api/prd/session/{id}` | GET | View session details |

## 本地运行数据

The following files are generated locally and should not be committed to GitHub:

```text
.env
data/sessions.json
exports/*.docx
exports/*.pdf
raw requirement documents
```

## 后续优化方向

### 1. PRD 多版本迭代管理

- 支持同一产品需求下生成多个 PRD 版本。
- 保留每次修改、补充和重新生成的历史记录。
- 支持版本命名，例如 v0.1 草稿版、v0.2 评审版、v1.0 开发确认版。
- 支持版本对比，帮助用户查看不同版本之间的需求变化。

### 2. PRD 在线编辑与局部优化

- 支持用户在页面中直接编辑 PRD 内容。
- 支持针对单个模块进行局部重写，例如只优化“功能模块”或“验收标准”。
- 支持根据用户补充的信息，自动更新对应章节，而不是每次重新生成整篇文档。

### 3. 模板精细化与行业适配

- 进一步细化不同产品类型的 PRD 模板。
- 增加更多行业模板，例如教育、金融、电商、医疗、企业 SaaS 等。
- 支持用户自定义模板结构，适配不同公司和团队的文档规范。

### 4. PRD 审核与评分机制

- 增加独立的 PRD 审核环节。
- 从完整性、清晰度、可开发性、可测试性、业务合理性、风险覆盖等维度评估 PRD 质量。
- 给出 PRD 总分和分项评分。
- 输出具体优化建议，告诉用户当前 PRD 缺少什么、哪里表达不清楚、下一步应该重点补充什么。
