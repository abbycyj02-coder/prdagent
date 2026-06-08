# PRD 生成 Agent MVP

一个本地可运行的 PRD 生成 Agent MVP。用户输入一句产品想法或关键词后，Agent 会通过产品类型识别、需求追问、完整度检查、PRD 生成和质量评审，输出标准化的中文 PRD，并支持导出 Word 和 PDF。

当前版本适合验证“从模糊需求到可评审 PRD”的核心效果，已接入 OpenAI LLM，同时保留本地规则和模板回退能力。

## 核心能力

- 输入关键词或一句产品想法，自动生成完整 PRD，而不是简单摘要。
- 支持软件 / AI Agent、智能硬件、政企合规三类需求识别。
- 支持像 ChatGPT 一样多轮追问，用户可以自然语言回答。
- 信息不足时不编造细节，在文档中明确写出“请补充 xxx 信息”。
- 生成内容按标准 PRD 主线组织：用户、场景、问题、MVP 范围、功能、验收、风险。
- 输出质量评审：完整性、清晰度、可开发性、可测试性、风险覆盖等维度。
- 支持 Word 和 PDF 导出。
- Word 标准化字体：中文宋体，英文 Calibri，字号小五。
- 本地保存历史会话，便于继续补充、重新生成和导出。

## 运行方式

### 1. 进入项目目录

```bash
cd /Users/abby/Desktop/prdagent
```

### 2. 配置环境变量

复制示例配置：

```bash
cp .env.example .env
```

编辑 `.env`：

```text
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-5.4
OPENAI_TIMEOUT=240
OPENAI_MAX_COMPLETION_TOKENS=12000
PRD_AGENT_USE_LLM=1
```

注意：不要把真实 API Key 提交到 GitHub。`.env` 已被 `.gitignore` 忽略。

### 3. 启动服务

```bash
./run.sh
```

也可以直接运行：

```bash
python3 -m backend.server
```

### 4. 打开网页

```text
http://127.0.0.1:8787
```

## 使用步骤

1. 在左侧输入产品想法，例如“做一个数字人生成平台”。
2. 点击“开始分析”，系统会识别产品类型和子类型。
3. 如果分类不准，可以手动修改产品类型和子类型。
4. 在“需求访谈”里自然语言回答 Agent 的追问。
5. 信息足够后点击“生成 PRD”，也可以在聊天里输入“可以了，生成 PRD”。
6. 在右侧预览和编辑 PRD。
7. 点击“重新评审”更新质量评分。
8. 点击“导出 Word”或“导出 PDF”下载文档。

## 简要设计思路

整体流程按一个产品经理写 PRD 的真实工作流拆成多个 Agent / 模块：

```text
用户输入
  -> Router Agent：识别产品类型和子类型
  -> Schema / Completeness Checker：判断信息完整度和缺失字段
  -> Clarification Agent：生成少量关键追问
  -> Chat Extractor：把自然语言回答沉淀为结构化字段
  -> PRD Generator：按产品类型生成标准 PRD
  -> Review Agent：评审文档质量并给出改进建议
  -> Export Service：导出 Word / PDF
```

设计重点：

- 用 Schema 控制追问和完整度，避免完全依赖模型自由发挥。
- 用强提示词约束 PRD 主线，减少章节堆砌和逻辑散乱。
- 对未知信息使用“请补充 xxx 信息”，避免把模型推断伪装成事实。
- LLM 调用失败时自动回退到本地规则和模板，保证 MVP 可跑通。
- 导出层独立处理 Word / PDF，方便后续扩展排版和企业模板。

## 代码结构

```text
backend/
  server.py                         # 本地 HTTP API 和静态文件服务
  models.py                         # 会话数据结构
  store.py                          # 本地 JSON 持久化
  agents/
    router_agent.py                 # 产品类型识别
    schema.py                       # 三类 PRD 字段 Schema
    completeness_checker.py         # 完整度评分
    clarification_agent.py          # 追问生成
    chat_agent.py                   # 对话提取和生成意图判断
    prd_generator.py                # PRD 生成
    review_agent.py                 # 质量评审
  services/
    llm_service.py                  # OpenAI 调用封装
    export_service.py               # Word / PDF 导出
public/
  index.html                        # Web 工作台
  app.js                            # 前端交互逻辑
  style.css                         # 前端样式
templates/                          # 本地回退模板
prompts/                            # 提示词草稿
scripts/                            # 辅助脚本
docs/
  prd_agent_mvp_operation_guide.md  # MVP 操作步骤文档
```

## API 概览

| 接口 | 方法 | 说明 |
|---|---|---|
| `/api/health` | GET | 服务健康检查 |
| `/api/prd/create` | POST | 创建 PRD 会话并识别类型 |
| `/api/prd/chat` | POST | 对话式补充需求或触发生成 |
| `/api/prd/answer` | POST | 提交结构化追问答案 |
| `/api/prd/update-type` | POST | 手动修改产品类型 |
| `/api/prd/generate` | POST | 生成 PRD 并评审 |
| `/api/prd/review` | POST | 对编辑后的 PRD 重新评审 |
| `/api/prd/export` | GET | 导出 Word 或 PDF |
| `/api/prd/history` | GET | 查看历史会话 |
| `/api/prd/session/{id}` | GET | 查看会话详情 |

## 运行数据

以下内容是本地运行生成的，不会提交到 GitHub：

- `.env`
- `data/sessions.json`
- `exports/*.docx`
- `exports/*.pdf`
- 原始需求 Word 文档

## 后续可扩展方向

- 迁移到 OpenAI Responses API，增强工具调用和长上下文状态管理。
- 增加企业自定义 PRD 模板和品牌排版。
- 增加人工确认清单，把“请补充 xxx 信息”转成可勾选事项。
- 增加版本对比、批注和多人协作。
- 支持将 PRD 继续拆解为用户故事、研发任务和测试用例。
