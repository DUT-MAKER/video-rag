// ViralCopilot AI Chatbot Studio Client Logic

let activeSessionId = null;
let activeAbortController = null;
let isStreaming = false;
let currentDraftScript = null;

// DOM Elements
const chatFeed = document.getElementById("chat-feed");
const emptyState = document.getElementById("empty-state");
const messagesList = document.getElementById("messages-list");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const stopBtn = document.getElementById("stop-btn");
const topKSelect = document.getElementById("top-k-select");
const sessionItems = document.getElementById("session-items");
const newChatBtn = document.getElementById("new-chat-btn");
const toggleSidebarBtn = document.getElementById("toggle-sidebar-btn");
const sidebar = document.getElementById("sidebar");
const toggleStudioBtn = document.getElementById("toggle-studio-btn");
const studioPanel = document.getElementById("studio-panel");
const closeStudioBtn = document.getElementById("close-studio-btn");
const studioEmpty = document.getElementById("studio-empty");
const studioBody = document.getElementById("studio-body");
const copyScriptMarkdownBtn = document.getElementById("copy-script-markdown-btn");
const downloadScriptJsonBtn = document.getElementById("download-script-json-btn");
const toastContainer = document.getElementById("toast-container");
const reingestBtn = document.getElementById("reingest-btn");

// Initialization
document.addEventListener("DOMContentLoaded", () => {
  loadSessions();
  setupEventListeners();
  autoResizeTextarea();
});

function setupEventListeners() {
  // Input triggers
  userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  userInput.addEventListener("input", autoResizeTextarea);

  sendBtn.addEventListener("click", sendMessage);
  stopBtn.addEventListener("click", stopStreaming);
  newChatBtn.addEventListener("click", startNewChat);

  // Quick Prompt Cards
  document.querySelectorAll(".quick-prompt-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const prompt = btn.getAttribute("data-prompt");
      if (prompt) {
        userInput.value = prompt;
        sendMessage();
      }
    });
  });

  // Toggle Sidebar on mobile
  toggleSidebarBtn.addEventListener("click", () => {
    sidebar.classList.toggle("-translate-x-full");
  });

  // Toggle Studio Panel
  toggleStudioBtn.addEventListener("click", () => {
    studioPanel.classList.toggle("hidden");
    if (!studioPanel.classList.contains("hidden")) {
      renderStudioScript(currentDraftScript);
    }
  });

  closeStudioBtn.addEventListener("click", () => {
    studioPanel.classList.add("hidden");
  });

  copyScriptMarkdownBtn.addEventListener("click", copyScriptMarkdown);
  downloadScriptJsonBtn.addEventListener("click", downloadScriptJson);

  reingestBtn.addEventListener("click", async () => {
    showToast("Refreshing knowledge benchmark patterns...", "info");
    try {
      const res = await fetch("/api/v1/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ file_path: "data/samples/sample_viral_videos.json" }),
      });
      const data = await res.json();
      if (data.success) {
        showToast(`Indexed ${data.data.total_indexed} benchmark patterns!`, "success");
      }
    } catch (e) {
      showToast("Failed to refresh benchmark store", "error");
    }
  });
}

function autoResizeTextarea() {
  userInput.style.height = "auto";
  userInput.style.height = Math.min(userInput.scrollHeight, 150) + "px";
}

// ----------------------------------------------------
// Toast Notification
// ----------------------------------------------------
function showToast(message, type = "info") {
  const toast = document.createElement("div");
  const bgClass =
    type === "success"
      ? "bg-emerald-500/90 text-white"
      : type === "error"
      ? "bg-rose-500/90 text-white"
      : "bg-slate-800/95 text-slate-100 border border-white/10";

  toast.className = `px-4 py-2.5 rounded-xl shadow-xl text-xs font-medium backdrop-blur-md transition-all duration-300 transform translate-y-2 opacity-0 pointer-events-auto ${bgClass}`;
  toast.innerText = message;
  toastContainer.appendChild(toast);

  requestAnimationFrame(() => {
    toast.classList.remove("translate-y-2", "opacity-0");
  });

  setTimeout(() => {
    toast.classList.add("opacity-0", "translate-y-2");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ----------------------------------------------------
// Session Management
// ----------------------------------------------------
async function loadSessions() {
  try {
    const res = await fetch("/api/v1/chat/sessions");
    const data = await res.json();
    if (data.success) {
      renderSessionList(data.data.session_ids);
    }
  } catch (err) {
    console.error("Failed to load sessions:", err);
  }
}

function renderSessionList(sessionIds) {
  sessionItems.innerHTML = "";
  if (!sessionIds || sessionIds.length === 0) {
    sessionItems.innerHTML = `<div class="text-[11px] text-slate-500 px-2 py-3">No active sessions yet</div>`;
    return;
  }

  sessionIds.forEach((id) => {
    const item = document.createElement("div");
    const isActive = id === activeSessionId;
    item.className = `group flex items-center justify-between px-2.5 py-2 rounded-lg text-xs transition-all cursor-pointer ${
      isActive
        ? "bg-blue-600/20 text-blue-300 font-medium border border-blue-500/30"
        : "text-slate-300 hover:bg-white/5"
    }`;

    item.innerHTML = `
      <div class="flex items-center space-x-2 truncate">
        <i data-lucide="message-square" class="w-3.5 h-3.5 shrink-0 ${isActive ? "text-blue-400" : "text-slate-400"}"></i>
        <span class="truncate">${id.substring(0, 8)}...</span>
      </div>
      <button class="delete-session-btn opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 transition-opacity" title="Delete session">
        <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
      </button>
    `;

    item.addEventListener("click", (e) => {
      if (!e.target.closest(".delete-session-btn")) {
        switchSession(id);
      }
    });

    const deleteBtn = item.querySelector(".delete-session-btn");
    deleteBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteSession(id);
    });

    sessionItems.appendChild(item);
  });

  lucide.createIcons();
}

async function switchSession(sessionId) {
  if (isStreaming) return;
  activeSessionId = sessionId;
  showToast(`Loading session ${sessionId.substring(0, 8)}...`, "info");

  try {
    const res = await fetch(`/api/v1/chat/sessions/${sessionId}`);
    const data = await res.json();
    if (data.success) {
      emptyState.classList.add("hidden");
      messagesList.innerHTML = "";

      const session = data.data;
      currentDraftScript = session.current_script;

      session.messages.forEach((msg) => {
        if (msg.role === "user") {
          appendUserMessage(msg.content);
        } else {
          appendAssistantHistoryMessage(msg.content, msg.referenced_patterns);
        }
      });

      renderStudioScript(currentDraftScript);
      loadSessions();
      scrollToBottom();
    }
  } catch (err) {
    showToast("Error loading session", "error");
  }
}

async function deleteSession(sessionId) {
  try {
    const res = await fetch(`/api/v1/chat/sessions/${sessionId}`, { method: "DELETE" });
    const data = await res.json();
    if (data.success) {
      showToast("Session deleted", "info");
      if (activeSessionId === sessionId) {
        startNewChat();
      }
      loadSessions();
    }
  } catch (err) {
    showToast("Failed to delete session", "error");
  }
}

function startNewChat() {
  if (isStreaming) return;
  activeSessionId = null;
  currentDraftScript = null;
  messagesList.innerHTML = "";
  emptyState.classList.remove("hidden");
  renderStudioScript(null);
  loadSessions();
  userInput.value = "";
  userInput.focus();
}

// ----------------------------------------------------
// Message Rendering & Sending
// ----------------------------------------------------
function scrollToBottom() {
  chatFeed.scrollTop = chatFeed.scrollHeight;
}

function appendUserMessage(text) {
  emptyState.classList.add("hidden");
  const msgDiv = document.createElement("div");
  msgDiv.className = "flex justify-end items-start space-x-3";
  msgDiv.innerHTML = `
    <div class="max-w-xl bg-blue-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm shadow-md text-sm leading-relaxed">
      ${escapeHtml(text)}
    </div>
    <div class="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center shrink-0 text-xs font-semibold text-slate-200">
      You
    </div>
  `;
  messagesList.appendChild(msgDiv);
  scrollToBottom();
}

function appendAssistantHistoryMessage(text, references) {
  emptyState.classList.add("hidden");
  const msgDiv = document.createElement("div");
  msgDiv.className = "flex justify-start items-start space-x-3";

  let refsHtml = "";
  if (references && references.length > 0) {
    refsHtml = renderBenchmarkCards(references);
  }

  msgDiv.innerHTML = `
    <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-primary to-brand-accent flex items-center justify-center shrink-0 shadow-md shadow-blue-500/20">
      <i data-lucide="sparkles" class="w-4 h-4 text-white"></i>
    </div>
    <div class="flex-1 max-w-2xl space-y-3">
      ${refsHtml}
      <div class="glass-panel p-4 rounded-2xl rounded-tl-sm text-sm prose-dark">
        ${marked.parse(text || "")}
      </div>
    </div>
  `;
  messagesList.appendChild(msgDiv);
  lucide.createIcons();
}

function renderBenchmarkCards(references) {
  let cards = references
    .map((ref) => {
      const scorePercent = Math.round((ref.similarity_score || 0.85) * 100);
      return `
      <div class="glass-card p-3 rounded-xl flex flex-col space-y-1.5 border border-white/10 hover:border-blue-500/40 transition-all text-xs">
        <div class="flex items-center justify-between">
          <span class="font-semibold text-slate-200 truncate pr-2">${escapeHtml(ref.original_caption || "Viral Pattern")}</span>
          <span class="px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-400 font-bold text-[10px] shrink-0 border border-blue-500/20">${scorePercent}% Match</span>
        </div>
        <div class="text-slate-400 line-clamp-2 italic text-[11px]">
          "${escapeHtml(ref.matched_hook || ref.summary || "")}"
        </div>
        ${
          ref.minio_video_url
            ? `<a href="${escapeHtml(ref.minio_video_url)}" target="_blank" class="text-blue-400 hover:text-blue-300 inline-flex items-center space-x-1 text-[11px] font-medium pt-0.5">
                <i data-lucide="external-link" class="w-3 h-3"></i>
                <span>Benchmark Video</span>
              </a>`
            : ""
        }
      </div>
    `;
    })
    .join("");

  return `
    <div class="space-y-1.5">
      <div class="flex items-center space-x-1.5 text-xs text-slate-400 font-medium">
        <i data-lucide="database" class="w-3.5 h-3.5 text-blue-400"></i>
        <span>Retrieved Viral Benchmarks:</span>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        ${cards}
      </div>
    </div>
  `;
}

// ----------------------------------------------------
// Real-Time SSE Token Streaming
// ----------------------------------------------------
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || isStreaming) return;

  userInput.value = "";
  autoResizeTextarea();
  appendUserMessage(text);

  // Set streaming state
  isStreaming = true;
  sendBtn.classList.add("hidden");
  stopBtn.classList.remove("hidden");

  // Create active assistant message container
  const msgDiv = document.createElement("div");
  msgDiv.className = "flex justify-start items-start space-x-3";
  msgDiv.innerHTML = `
    <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-primary to-brand-accent flex items-center justify-center shrink-0 shadow-md shadow-blue-500/20">
      <i data-lucide="sparkles" class="w-4 h-4 text-white"></i>
    </div>
    <div class="flex-1 max-w-2xl space-y-3">
      <div class="metadata-slot"></div>
      <div class="glass-panel p-4 rounded-2xl rounded-tl-sm text-sm prose-dark streaming-cursor">
        <span class="typing-slot flex items-center space-x-1 py-1">
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
          <span class="typing-dot"></span>
        </span>
        <div class="content-slot hidden"></div>
      </div>
    </div>
  `;
  messagesList.appendChild(msgDiv);
  lucide.createIcons();
  scrollToBottom();

  const metadataSlot = msgDiv.querySelector(".metadata-slot");
  const streamingBubble = msgDiv.querySelector(".glass-panel");
  const typingSlot = msgDiv.querySelector(".typing-slot");
  const contentSlot = msgDiv.querySelector(".content-slot");

  activeAbortController = new AbortController();
  let accumulatedMarkdown = "";
  const topK = parseInt(topKSelect.value, 10) || 3;

  try {
    const response = await fetch("/api/v1/chat/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_id: activeSessionId,
        top_k_references: topK,
      }),
      signal: activeAbortController.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP Error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith("data:")) continue;

        const payloadStr = trimmed.substring(5).trim();
        if (payloadStr === "[DONE]") {
          break;
        }

        try {
          const chunk = JSON.parse(payloadStr);

          if (chunk.event === "metadata") {
            activeSessionId = chunk.session_id;
            let metaHeader = `
              <div class="flex items-center space-x-2 text-[11px] font-medium text-slate-400">
                <span class="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-wider">${chunk.intent || "Co-Pilot"}</span>
                <span>Session: ${chunk.session_id.substring(0, 8)}</span>
              </div>
            `;

            let refsHtml = "";
            if (chunk.referenced_patterns && chunk.referenced_patterns.length > 0) {
              refsHtml = renderBenchmarkCards(chunk.referenced_patterns);
            }
            metadataSlot.innerHTML = `${metaHeader}${refsHtml ? `<div class="mt-2">${refsHtml}</div>` : ""}`;
            lucide.createIcons();
          } else if (chunk.event === "token") {
            typingSlot.classList.add("hidden");
            contentSlot.classList.remove("hidden");
            accumulatedMarkdown += chunk.token;
            contentSlot.innerHTML = marked.parse(accumulatedMarkdown);
            scrollToBottom();
          }
        } catch (e) {
          console.warn("Error parsing chunk payload:", e);
        }
      }
    }
  } catch (err) {
    if (err.name !== "AbortError") {
      contentSlot.classList.remove("hidden");
      typingSlot.classList.add("hidden");
      contentSlot.innerHTML += `<div class="text-rose-400 text-xs mt-2">Error connecting to assistant. Please try again.</div>`;
    }
  } finally {
    // End of streaming cleanup
    streamingBubble.classList.remove("streaming-cursor");
    isStreaming = false;
    sendBtn.classList.remove("hidden");
    stopBtn.classList.add("hidden");
    activeAbortController = null;
    loadSessions();

    // Check if output looks like a viral script and update studio
    parseAndSyncScriptStudio(accumulatedMarkdown);
  }
}

function stopStreaming() {
  if (activeAbortController) {
    activeAbortController.abort();
    showToast("Streaming stopped", "info");
  }
}

// ----------------------------------------------------
// Script Studio Inspector
// ----------------------------------------------------
function parseAndSyncScriptStudio(markdown) {
  if (!markdown) return;
  // If response contains scenes or hook keywords, extract or synthesize preview
  if (markdown.includes("Hook") || markdown.includes("Scene") || markdown.includes("Kịch bản")) {
    studioPanel.classList.remove("hidden");
    renderStudioMarkdownPreview(markdown);
  }
}

function renderStudioMarkdownPreview(markdown) {
  studioEmpty.classList.add("hidden");
  studioBody.classList.remove("hidden");
  studioBody.innerHTML = `
    <div class="glass-card p-3 rounded-xl space-y-2 border-l-4 border-brand-cta">
      <div class="font-bold text-slate-100">Live Draft Preview</div>
      <div class="text-slate-300 prose-dark text-xs">${marked.parse(markdown)}</div>
    </div>
  `;
}

function renderStudioScript(script) {
  if (!script) {
    studioEmpty.classList.remove("hidden");
    studioBody.classList.add("hidden");
    return;
  }

  studioEmpty.classList.add("hidden");
  studioBody.classList.remove("hidden");

  const scenesHtml = (script.scenes || [])
    .map(
      (s) => `
    <div class="glass-card p-3 rounded-xl space-y-2 border border-white/10">
      <div class="flex items-center justify-between text-[11px] font-semibold text-blue-400">
        <span>Scene ${s.scene_number} (${s.time_range})</span>
        <span class="text-slate-400">${s.audio_sfx_cue || ""}</span>
      </div>
      <div class="text-slate-200"><strong>Narration:</strong> ${escapeHtml(s.narration)}</div>
      <div class="text-slate-400"><strong>Visual:</strong> ${escapeHtml(s.visual_action)}</div>
      ${
        s.image_prompt
          ? `<div class="bg-black/40 p-2 rounded-lg text-[11px] font-mono text-cyan-300 flex items-center justify-between">
              <span class="truncate pr-2">${escapeHtml(s.image_prompt)}</span>
              <button onclick="copyToClipboard('${escapeJsString(s.image_prompt)}')" class="text-slate-400 hover:text-white shrink-0 p-1" title="Copy Midjourney Prompt">
                <i data-lucide="copy" class="w-3.5 h-3.5"></i>
              </button>
            </div>`
          : ""
      }
    </div>
  `
    )
    .join("");

  studioBody.innerHTML = `
    <div class="space-y-3">
      <div>
        <h2 class="text-base font-bold text-white">${escapeHtml(script.title || "Viral Script")}</h2>
        <div class="flex items-center space-x-2 mt-1">
          <span class="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 text-[10px] font-semibold">${script.platform || "tiktok"}</span>
          <span class="px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-300 text-[10px] font-semibold">${script.target_duration_seconds || 45}s</span>
        </div>
      </div>

      ${
        script.hook
          ? `<div class="glass-card p-3 rounded-xl space-y-1 border-l-4 border-brand-cta">
              <div class="text-[10px] uppercase tracking-wider text-orange-400 font-bold">3s Retention Hook (${script.hook.hook_type || ""})</div>
              <div class="text-slate-100 font-medium">"${escapeHtml(script.hook.script || "")}"</div>
              <div class="text-[11px] text-slate-400">${escapeHtml(script.hook.retention_rationale || "")}</div>
            </div>`
          : ""
      }

      <div class="space-y-2">
        <div class="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Storyboard Scenes</div>
        ${scenesHtml}
      </div>
    </div>
  `;
  lucide.createIcons();
}

function copyScriptMarkdown() {
  const content = studioBody.innerText;
  if (!content) {
    showToast("No script to copy", "info");
    return;
  }
  copyToClipboard(content);
}

function downloadScriptJson() {
  if (!currentDraftScript) {
    showToast("No structured script to download", "info");
    return;
  }
  const blob = new Blob([JSON.stringify(currentDraftScript, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `viral_script_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast("Script JSON downloaded!", "success");
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showToast("Copied to clipboard!", "success");
  });
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function escapeJsString(str) {
  if (!str) return "";
  return str.replace(/\/g, "\\").replace(/'/g, "\'").replace(/\"/g, "\\\"");
}
