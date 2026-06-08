const state = {
  session: null,
  history: [],
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderText(value) {
  return escapeHtml(value).replace(/\n/g, "<br />");
}

function toast(message) {
  const node = $("#toast");
  node.textContent = message;
  node.classList.add("show");
  clearTimeout(window.__toastTimer);
  window.__toastTimer = setTimeout(() => node.classList.remove("show"), 2600);
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

function shortText(value, length = 42) {
  if (!value) return "";
  return value.length > length ? `${value.slice(0, length)}...` : value;
}

function typeName(type) {
  return {
    software: "软件 / AI Agent",
    hardware: "智能硬件",
    enterprise: "政企合规",
  }[type] || "待识别";
}

function statusName(status) {
  return {
    created: "已创建",
    routed: "已分类",
    need_clarification: "待补充",
    ready_to_generate: "可生成",
    generating: "生成中",
    reviewed: "已评审",
    exported: "已导出",
  }[status] || status || "未创建";
}

function renderHistory() {
  const list = $("#historyList");
  if (!state.history.length) {
    list.innerHTML = `<div class="empty-state">暂无历史会话。</div>`;
    return;
  }
  list.innerHTML = state.history
    .map((item) => {
      const active = state.session && item.session_id === state.session.session_id ? "active" : "";
      return `
        <button class="history-item ${active}" data-session="${item.session_id}">
          <strong>${shortText(item.sub_type || typeName(item.product_type), 24)}</strong>
          <span>${typeName(item.product_type)} · ${item.completeness_score || 0}/100</span>
        </button>
      `;
    })
    .join("");

  $$(".history-item").forEach((btn) => {
    btn.addEventListener("click", () => loadSession(btn.dataset.session));
  });
}

function renderRoute() {
  const session = state.session;
  if (!session) {
    $("#routeContent").innerHTML = "创建会话后显示产品类型、子类型和缺失信息。";
    $("#confidenceBadge").textContent = "待识别";
    return;
  }

  $("#confidenceBadge").textContent = `${Math.round(session.confidence * 100)}%`;
  $("#confidenceBadge").className = session.confidence < 0.7 ? "status-pill warn" : "status-pill";

  const missing = (session.missing_fields || []).length;
  const reasons = (session.route_reasons || []).map((item) => `<li>${item}</li>`).join("");

  $("#routeContent").innerHTML = `
    <div class="route-grid">
      <div class="field-block">
        <label>产品类型</label>
        <select id="typeSelect">
          <option value="software" ${session.product_type === "software" ? "selected" : ""}>软件 / AI Agent</option>
          <option value="hardware" ${session.product_type === "hardware" ? "selected" : ""}>智能硬件</option>
          <option value="enterprise" ${session.product_type === "enterprise" ? "selected" : ""}>政企合规</option>
        </select>
      </div>
      <div class="field-block">
        <label>子类型</label>
        <input id="subTypeInput" value="${session.sub_type || ""}" />
      </div>
    </div>
    <div class="button-row compact">
      <button class="secondary" id="updateTypeBtn">确认类型</button>
    </div>
    <div class="list-section">
      <h4>分类依据</h4>
      <ul>${reasons || "<li>暂无分类依据</li>"}</ul>
    </div>
    <div class="list-section">
      <h4>当前缺失</h4>
      <p class="hint">${missing ? `还有 ${missing} 个关键字段未补齐。` : "关键字段已补齐到可生成状态。"}</p>
    </div>
  `;

  $("#updateTypeBtn").addEventListener("click", updateType);
}

function renderQuestions() {
  const session = state.session;
  const score = session ? session.completeness_score || 0 : 0;
  $("#scoreBadge").textContent = `${score}/100`;
  $("#scoreBadge").className = score >= 70 ? "status-pill" : score >= 40 ? "status-pill warn" : "status-pill muted";
  $("#scoreBar").style.width = `${score}%`;

  if (!session) {
    $("#questionContent").innerHTML = `<div class="chat-empty">创建会话后，Agent 会像产品访谈一样追问关键问题。</div>`;
    return;
  }

  const messages = session.chat_messages || [];
  const answers = session.answers || {};
  const answered = Object.entries(answers)
    .filter(([key]) => !key.startsWith("_"))
    .slice(0, 6)
    .map(([key, value]) => `<span>${escapeHtml(key)}：${escapeHtml(value)}</span>`)
    .join("");
  $("#questionContent").innerHTML = `
    <div class="chat-box" id="chatBox">
      ${messages
        .map(
          (message) => `
            <div class="chat-message ${message.role === "user" ? "user" : "assistant"}">
              <div class="chat-role">${message.role === "user" ? "你" : "PRD Agent"}</div>
              <div class="chat-bubble">${renderText(message.content)}</div>
            </div>
          `
        )
        .join("")}
    </div>
    <form id="chatForm" class="chat-form">
      <textarea id="chatInput" placeholder="像聊天一样回答：目标用户是产品经理和创业者，MVP 先做输入、追问、生成、评审和 Word 导出..."></textarea>
      <div class="button-row compact">
        <button class="primary" type="submit">发送回答</button>
        <button class="secondary" type="button" id="chatGenerateBtn">可以了，生成 PRD</button>
      </div>
    </form>
    <div class="answer-chips">${answered || "<span>还没有沉淀结构化答案</span>"}</div>
  `;

  const chatBox = $("#chatBox");
  chatBox.scrollTop = chatBox.scrollHeight;
  $("#chatForm").addEventListener("submit", sendChatMessage);
  $("#chatGenerateBtn").addEventListener("click", () => sendChatMessage(null, "可以了，直接生成完整详细 PRD"));
}

function renderPreview() {
  const session = state.session;
  $("#sessionStatus").textContent = session ? statusName(session.status) : "未创建";
  $("#sessionStatus").className = session ? "status-pill" : "status-pill muted";
  $("#generateBtn").disabled = !session;
  $("#reviewBtn").disabled = !session || !session.prd_markdown;
  $("#exportDocxBtn").disabled = !session || !session.prd_markdown;
  $("#exportPdfBtn").disabled = !session || !session.prd_markdown;
  $("#prdPreview").value = session ? session.prd_markdown || "" : "";
  renderReview();
}

function renderReview() {
  const report = state.session && state.session.quality_report;
  if (!report || !Object.keys(report).length) {
    $("#reviewContent").innerHTML = "生成 PRD 后显示完整性、清晰度、可开发性、风险和建议。";
    return;
  }
  const dimensions = report.dimension_scores || {};
  const dimensionHtml = Object.entries(dimensions)
    .map(
      ([name, score]) => `
        <div class="metric">
          <strong>${score}</strong>
          <span>${name}</span>
        </div>
      `
    )
    .join("");

  const list = (items) => (items && items.length ? items.map((item) => `<li>${typeof item === "string" ? item : `${item.name}：${item.mitigation}`}</li>`).join("") : "<li>暂无</li>");

  $("#reviewContent").innerHTML = `
    <div class="review-grid">
      <div class="metric">
        <strong>${report.quality_score}</strong>
        <span>综合评分</span>
      </div>
      <div class="metric">
        <strong>${report.pending_count}</strong>
        <span>待确认项</span>
      </div>
      <div class="metric">
        <strong>${(report.ambiguous_terms || []).length}</strong>
        <span>模糊词</span>
      </div>
      ${dimensionHtml}
    </div>
    <div class="list-section">
      <h4>缺失项</h4>
      <ul>${list(report.missing_items)}</ul>
    </div>
    <div class="list-section">
      <h4>模糊表达</h4>
      <ul>${list(report.ambiguous_terms)}</ul>
    </div>
    <div class="list-section">
      <h4>风险</h4>
      <ul>${list(report.risks)}</ul>
    </div>
    <div class="list-section">
      <h4>优化建议</h4>
      <ul>${list(report.suggestions)}</ul>
    </div>
  `;
}

function renderAll() {
  renderHistory();
  renderRoute();
  renderQuestions();
  renderPreview();
}

async function refreshHistory() {
  state.history = await api("/api/prd/history");
  renderHistory();
}

async function checkHealth() {
  try {
    const data = await api("/api/health");
    $("#health").textContent = data.llm_enabled ? `LLM 已启用 · ${data.model}` : "本地模板模式";
  } catch (err) {
    $("#health").textContent = "服务不可用";
  }
}

async function createSession() {
  const userInput = $("#ideaInput").value.trim();
  if (!userInput) {
    toast("请先输入产品想法");
    return;
  }
  $("#createBtn").disabled = true;
  try {
    state.session = await api("/api/prd/create", {
      method: "POST",
      body: JSON.stringify({ user_input: userInput, language: "zh-CN" }),
    });
    toast("已完成需求分类");
    await refreshHistory();
    renderAll();
  } catch (err) {
    toast(err.message);
  } finally {
    $("#createBtn").disabled = false;
  }
}

async function loadSession(sessionId) {
  state.session = await api(`/api/prd/session/${sessionId}`);
  $("#ideaInput").value = state.session.user_input;
  renderAll();
}

async function updateType() {
  if (!state.session) return;
  state.session = await api("/api/prd/update-type", {
    method: "POST",
    body: JSON.stringify({
      session_id: state.session.session_id,
      product_type: $("#typeSelect").value,
      sub_type: $("#subTypeInput").value,
    }),
  });
  toast("产品类型已更新");
  await refreshHistory();
  renderAll();
}

async function submitAnswers(event) {
  event.preventDefault();
  if (!state.session) return;
  const answers = {};
  $$("#answerForm textarea").forEach((node) => {
    answers[node.dataset.field] = node.value.trim();
  });
  state.session = await api("/api/prd/answer", {
    method: "POST",
    body: JSON.stringify({ session_id: state.session.session_id, answers }),
  });
  toast("回答已提交");
  await refreshHistory();
  renderAll();
}

async function sendChatMessage(event, forcedMessage = "") {
  if (event) event.preventDefault();
  if (!state.session) return;
  const input = $("#chatInput");
  const message = forcedMessage || (input ? input.value.trim() : "");
  if (!message) {
    toast("请输入回答内容");
    return;
  }
  const buttons = $$("#chatForm button");
  buttons.forEach((btn) => (btn.disabled = true));
  try {
    state.session = await api("/api/prd/chat", {
      method: "POST",
      body: JSON.stringify({
        session_id: state.session.session_id,
        message,
      }),
    });
    if (state.session.generated_now) {
      toast("已根据对话生成完整 PRD");
    } else {
      toast("已理解并更新需求");
    }
    await refreshHistory();
    renderAll();
  } catch (err) {
    toast(err.message);
  } finally {
    buttons.forEach((btn) => (btn.disabled = false));
  }
}

async function generatePrd() {
  if (!state.session) return;
  $("#generateBtn").disabled = true;
  try {
    state.session = await api("/api/prd/generate", {
      method: "POST",
      body: JSON.stringify({ session_id: state.session.session_id }),
    });
    toast("PRD 已生成并评审");
    await refreshHistory();
    renderAll();
  } catch (err) {
    toast(err.message);
  } finally {
    $("#generateBtn").disabled = false;
  }
}

async function reviewEditedPrd() {
  if (!state.session) return;
  state.session = await api("/api/prd/review", {
    method: "POST",
    body: JSON.stringify({
      session_id: state.session.session_id,
      prd_markdown: $("#prdPreview").value,
    }),
  });
  toast("已重新评审");
  await refreshHistory();
  renderAll();
}

async function exportFile(type) {
  if (!state.session) return;
  const result = await api(`/api/prd/export?session_id=${state.session.session_id}&type=${type}`);
  toast(`已生成 ${result.filename}`);
  window.open(result.url, "_blank");
  await refreshHistory();
}

function newSession() {
  state.session = null;
  $("#ideaInput").value = "";
  renderAll();
}

function bindEvents() {
  $("#createBtn").addEventListener("click", createSession);
  $("#clearBtn").addEventListener("click", () => ($("#ideaInput").value = ""));
  $("#newBtn").addEventListener("click", newSession);
  $("#generateBtn").addEventListener("click", generatePrd);
  $("#reviewBtn").addEventListener("click", reviewEditedPrd);
  $("#exportDocxBtn").addEventListener("click", () => exportFile("docx"));
  $("#exportPdfBtn").addEventListener("click", () => exportFile("pdf"));
  $$("[data-example]").forEach((btn) => {
    btn.addEventListener("click", () => {
      $("#ideaInput").value = btn.dataset.example;
    });
  });
}

async function init() {
  bindEvents();
  renderAll();
  await checkHealth();
  await refreshHistory();
}

init();
