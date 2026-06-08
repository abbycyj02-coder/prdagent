# PRD Agent MVP

An AI-powered PRD generation agent that turns rough product ideas into structured, review-ready PRD documents with clarification, completeness checking, quality review, and Word/PDF export.

PRD Agent 是一个面向产品经理的本地可运行 AI Agent MVP。用户只需要输入一句产品想法或关键词，系统会自动识别产品类型、追问缺失信息、检查需求完整度，并生成结构化中文 PRD 文档。最终结果支持在线预览、质量评审、编辑以及 Word / PDF 导出。

该项目的核心目标是验证：AI 是否可以辅助产品经理完成从“模糊需求”到“可评审 PRD 初稿”的工作流。

---

## Core Features / 核心能力

### 1. Product Requirement Understanding / 需求理解

- 支持输入一句产品想法或关键词，自动识别产品类型。
- 当前支持三类 PRD 场景：
  - 软件 / AI Agent 产品
  - 智能硬件产品
  - 政企 / ToB / 合规类系统
- 支持手动修改产品类型和子类型，避免自动分类错误影响后续生成。

### 2. Multi-agent PRD Workflow / 多 Agent 工作流

系统将产品经理写 PRD 的过程拆解为多个模块：

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

### 3. Clarification & Completeness Check / 追问与完整度检查

- 当需求信息不足时，系统会生成少量关键追问。
- 用户可以像和 ChatGPT 对话一样自然语言补充需求。
- 系统会将用户回答沉淀为结构化字段。
- 对未知信息不会直接编造，而是在文档中标记“请补充 xxx 信息”。

### 4. PRD Generation / PRD 生成

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

### 5. Review & Export / 质量评审与导出

- 支持从完整性、清晰度、可开发性、可测试性、风险覆盖等维度进行 PRD 质量评审。
- 支持导出 Word 和 PDF。
- Word 导出采用标准化字体设置：中文宋体，英文 Calibri，字号小五。
- 本地保存历史会话，方便继续补充、重新生成和导出。

---

## Project Highlights / 项目亮点

- 设计了从需求识别、信息补全、PRD 生成到质量评审的完整 Agent 工作流。
- 使用 Schema 控制追问和完整度检查，避免完全依赖模型自由发挥。
- 通过产品类型路由，让不同产品方向使用不同 PRD 结构。
- 在信息不足时显式标记待补充内容，减少 LLM 幻觉。
- 实现 Word / PDF 导出，使生成结果从聊天文本变成可交付文档。
- LLM 调用失败时保留本地规则和模板回退能力，保证 MVP 可运行。

---

## Tech Stack / 技术栈

- Backend: Python
- Frontend: HTML, CSS, JavaScript
- LLM: OpenAI API
- Storage: Local JSON session storage
- Export: Word / PDF export service
- Architecture: Multi-agent workflow + Schema-based requirement checking

---

## Getting Started / 运行方式

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

## Usage / 使用步骤

1. Enter a product idea, such as “做一个数字人生成平台”.
2. Click “开始分析”.
3. The system identifies the product type and subtype.
4. If the classification is inaccurate, manually adjust it.
5. Answer the clarification questions in natural language.
6. Click “生成 PRD” or type “可以了，生成 PRD”.
7. Preview and edit the PRD on the right side.
8. Click “重新评审” to update the quality score.
9. Export the final document as Word or PDF.

---

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

---

## Local Runtime Data / 本地运行数据

The following files are generated locally and should not be committed to GitHub:

```text
.env
data/sessions.json
exports/*.docx
exports/*.pdf
raw requirement documents
```

---

## Future Improvements / 后续可扩展方向

- Migrate to OpenAI Responses API for better tool calling and long-context state management.
- Add enterprise-specific PRD templates and branded document styles.
- Convert missing information into a checklist for human confirmation.
- Add version comparison, comments, and collaborative review.
- Extend PRD output into user stories, development tasks, and test cases.
- Add more product categories and industry-specific PRD templates.
