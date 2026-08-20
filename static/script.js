const messages = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const questionInput = document.querySelector("#question");
const pdfInput = document.querySelector("#pdf-input");
const dropZone = document.querySelector("#drop-zone");
const documentStatus = document.querySelector("#document-status");
const attachmentChip = document.querySelector("#attachment-chip");
const voiceButton = document.querySelector("#voice-button");
const composerHint = document.querySelector("#composer-hint");
const authScreen = document.querySelector("#auth-screen");
const appShell = document.querySelector("#app-shell");
const loginForm = document.querySelector("#login-form");
const signupForm = document.querySelector("#signup-form");
const loginTab = document.querySelector("#login-tab");
const signupTab = document.querySelector("#signup-tab");
const authError = document.querySelector("#auth-error");
let documentText = "";
let documentName = "";
let speechRecognition = null;
let isListening = false;

function addMessage(role, content, meta = "") {
	const item = document.createElement("article");
	item.className = `message ${role}`;
	item.innerHTML = `<div class="avatar">${role === "user" ? "Y" : "S"}</div><div><div class="bubble"></div><div class="message-meta">${meta}</div></div>`;
	item.querySelector(".bubble").textContent = content;
	messages.appendChild(item);
	messages.scrollTop = messages.scrollHeight;
	return item;
}

function showToast(message) {
	const toast = document.querySelector("#toast");
	toast.textContent = message;
	toast.classList.add("show");
	window.clearTimeout(showToast.timeout);
	showToast.timeout = window.setTimeout(() => toast.classList.remove("show"), 4200);
}

function clearDocument() {
	documentText = "";
	documentName = "";
	pdfInput.value = "";
	dropZone.classList.remove("hidden");
	documentStatus.classList.add("hidden");
	attachmentChip.classList.add("hidden");
	document.querySelector("#file-count").textContent = "0 / 1";
}

function setDocument(filename, text) {
	documentName = filename;
	documentText = text;
	document.querySelector("#document-title").textContent = filename;
	document.querySelector("#document-meta").textContent = `${text.length.toLocaleString()} characters ready`;
	document.querySelector("#attachment-name").textContent = filename;
	document.querySelector("#file-count").textContent = "1 / 1";
	dropZone.classList.add("hidden");
	documentStatus.classList.remove("hidden");
	attachmentChip.classList.remove("hidden");
}

async function loadHistory() {
	try {
		const response = await fetch("/api/history");
		if (response.status === 401) return;
		const data = await response.json();
		renderHistory(data.items || []);
		if (data.messages.length) data.messages.forEach((message) => addMessage(message.role, message.content, message.role === "user" ? "You" : "Studyroom"));
		else addMessage("assistant", "Welcome to your private study desk. Ask me anything, or attach a PDF and I’ll help you work through it.", "Studyroom · just now");
	} catch (error) {
		addMessage("assistant", "Your workspace is ready. Start Ollama locally when you are ready to ask a question.", "Studyroom");
	}
}

async function refreshHistory() {
	try {
		const response = await fetch("/api/history");
		if (!response.ok) return;
		const data = await response.json();
		renderHistory(data.items || []);
	} catch (error) {
		showToast("History could not be refreshed.");
	}
}

function renderHistory(items) {
	const historyList = document.querySelector("#history-list");
	historyList.innerHTML = "";
	if (!items.length) {
		historyList.innerHTML = '<div class="history-empty">Your questions will appear here.</div>';
		return;
	}
	items.forEach((item) => historyList.appendChild(createHistoryButton(item)));
}

function createHistoryButton(item) {
	const button = document.createElement("div");
	button.className = "history-item";
	button.setAttribute("role", "button");
	button.tabIndex = 0;
	const date = new Date(`${item.created_at.replace(" ", "T")}Z`);
	const label = item.kind === "document" ? "PDF uploaded" : (item.document_name ? `Question · ${item.document_name}` : "Question");
	button.innerHTML = `<div class="history-copy"><strong></strong><small>${label} · ${date.toLocaleDateString()}</small></div><button class="history-delete" type="button" aria-label="Delete history item" title="Remove from history">×</button>`;
	button.querySelector("strong").textContent = item.title;
	button.addEventListener("click", (event) => {
		if (event.target.closest(".history-delete")) return;
		item.pending ? (questionInput.value = item.title, questionInput.focus()) : openHistoryItem(item);
	});
	button.addEventListener("keydown", (event) => {
		if ((event.key === "Enter" || event.key === " ") && event.target === button) {
			event.preventDefault();
			item.pending ? (questionInput.value = item.title, questionInput.focus()) : openHistoryItem(item);
		}
	});
	button.querySelector(".history-delete").addEventListener("click", () => deleteHistoryItem(item, button));
	return button;
}

async function deleteHistoryItem(item, element) {
	if (item.pending) {
		element.remove();
		return;
	}
	if (!window.confirm("Remove this item from your visible history? The backend record will be retained.")) return;
	try {
		const response = await fetch(`/api/history/${item.kind}/${item.id}`, { method: "DELETE" });
		const data = await response.json();
		if (!response.ok) throw new Error(data.error || "Could not remove this history item.");
		element.remove();
		if (!document.querySelector(".history-item")) renderHistory([]);
		messages.innerHTML = "";
		addMessage("assistant", "That item was removed from visible history. The permanent backend record is still retained.", "Studyroom · history updated");
	} catch (error) {
		showToast(error.message);
	}
}

function prependHistoryItem(item) {
	const historyList = document.querySelector("#history-list");
	historyList.querySelector(".history-empty")?.remove();
	historyList.prepend(createHistoryButton(item));
}

async function openHistoryItem(item) {
	try {
		const response = await fetch("/api/history");
		if (!response.ok) throw new Error("Please log in again to open history.");
		const data = await response.json();
		messages.innerHTML = "";
		if (item.kind === "document") {
			addMessage("assistant", `${item.title} was uploaded to your study workspace. Attach it again in the document panel to ask a new question about it.`, "Studyroom · PDF activity");
			return;
		}
		const messageIndex = data.messages.findIndex((message) => message.id === item.id && message.role === "user");
		if (messageIndex < 0) throw new Error("That history item is no longer available.");
		const question = data.messages[messageIndex];
		addMessage("user", question.content, "You · saved question");
		const answer = data.messages[messageIndex + 1];
		if (answer && answer.role === "assistant") addMessage("assistant", answer.content, "Studyroom · saved answer");
		questionInput.value = question.content;
		questionInput.dispatchEvent(new Event("input"));
		questionInput.focus();
	} catch (error) {
		showToast(error.message);
	}
}

function showAuthMode(mode) {
	const loginMode = mode === "login";
	loginTab.classList.toggle("active", loginMode);
	signupTab.classList.toggle("active", !loginMode);
	loginForm.classList.toggle("hidden", !loginMode);
	signupForm.classList.toggle("hidden", loginMode);
	document.querySelector("#auth-title").textContent = loginMode ? "Welcome back" : "Create your account";
	document.querySelector("#auth-subtitle").textContent = loginMode ? "Continue your study session." : "Start your private study workspace.";
	authError.classList.add("hidden");
}

function showWorkspace(user) {
	authScreen.classList.add("hidden");
	appShell.classList.remove("hidden");
	document.querySelector("#user-name").textContent = user.name;
	document.querySelector("#user-email").textContent = user.email;
	document.querySelector("#user-avatar").textContent = user.name.charAt(0).toUpperCase();
	messages.innerHTML = "";
	loadHistory();
}

function showAuthError(message) {
	authError.textContent = message;
	authError.classList.remove("hidden");
}

async function submitAuth(url, payload) {
	const response = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
	const data = await response.json();
	if (!response.ok) throw new Error(data.error || "Authentication failed.");
	return data;
}

loginTab.addEventListener("click", () => showAuthMode("login"));
signupTab.addEventListener("click", () => showAuthMode("signup"));
loginForm.addEventListener("submit", async (event) => {
	event.preventDefault();
	try {
		const data = await submitAuth("/api/auth/login", { email: document.querySelector("#login-email").value, password: document.querySelector("#login-password").value });
		showWorkspace(data.user);
	} catch (error) { showAuthError(error.message); }
});
signupForm.addEventListener("submit", async (event) => {
	event.preventDefault();
	try {
		const data = await submitAuth("/api/auth/signup", { name: document.querySelector("#signup-name").value, email: document.querySelector("#signup-email").value, password: document.querySelector("#signup-password").value });
		showWorkspace(data.user);
	} catch (error) { showAuthError(error.message); }
});
document.querySelector("#logout-button").addEventListener("click", async () => {
	await fetch("/api/auth/logout", { method: "POST" });
	appShell.classList.add("hidden");
	authScreen.classList.remove("hidden");
	loginForm.reset();
	showAuthMode("login");
});

async function uploadFile(file) {
	if (!file) return;
	if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) return showToast("Please choose a PDF file.");
	const body = new FormData();
	body.append("file", file);
	try {
		const response = await fetch("/api/upload", { method: "POST", body });
		const data = await response.json();
		if (!response.ok) throw new Error(data.error || "Upload failed.");
		setDocument(data.filename, data.text);
	} catch (error) {
		showToast(error.message);
	}
}

form.addEventListener("submit", async (event) => {
	event.preventDefault();
	const question = questionInput.value.trim();
	if (!question) return questionInput.focus();
	addMessage("user", question, "You · just now");
	prependHistoryItem({ kind: "question", title: question, document_name: documentName, created_at: new Date().toISOString().replace("T", " ").slice(0, 19), pending: true });
	questionInput.value = "";
	questionInput.style.height = "auto";
	const typing = addMessage("assistant", "Thinking with your local model...", "Studyroom");
	typing.querySelector(".bubble").classList.add("typing");
	try {
		const response = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question, document_text: documentText, document_name: documentName }) });
		const data = await response.json();
		typing.remove();
		if (!response.ok) throw new Error(data.error || "The assistant could not respond.");
		addMessage("assistant", data.answer, "Studyroom · just now");
		refreshHistory();
	} catch (error) {
		typing.remove();
		showToast(error.message);
		addMessage("assistant", "I couldn’t reach the local model. Make sure Ollama is running and llama3.2:3b is installed.", "Studyroom");
		refreshHistory();
	}
});

questionInput.addEventListener("input", () => { questionInput.style.height = "auto"; questionInput.style.height = `${Math.min(questionInput.scrollHeight, 120)}px`; });
questionInput.addEventListener("keydown", (event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); form.requestSubmit(); } });
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (SpeechRecognition) {
	speechRecognition = new SpeechRecognition();
	speechRecognition.lang = navigator.language || "en-US";
	speechRecognition.interimResults = true;
	speechRecognition.maxAlternatives = 1;
	speechRecognition.onstart = () => {
		isListening = true;
		voiceButton.classList.add("listening");
		voiceButton.setAttribute("aria-label", "Stop voice input");
		voiceButton.title = "Stop listening";
		composerHint.textContent = "Listening... speak your question, then press the microphone to stop.";
	};
	speechRecognition.onresult = (event) => {
		questionInput.value = Array.from(event.results).map((result) => result[0].transcript).join("");
		questionInput.dispatchEvent(new Event("input"));
	};
	speechRecognition.onerror = (event) => {
		if (event.error !== "aborted") showToast(event.error === "not-allowed" ? "Microphone access was blocked. Allow it in your browser settings." : "Voice input could not hear that. Please try again.");
	};
	speechRecognition.onend = () => {
		isListening = false;
		voiceButton.classList.remove("listening");
		voiceButton.setAttribute("aria-label", "Start voice input");
		voiceButton.title = "Speak your question";
		composerHint.innerHTML = "Press <kbd>Enter</kbd> to send <span>•</span> <kbd>Shift + Enter</kbd> for a new line";
	};
	voiceButton.addEventListener("click", () => isListening ? speechRecognition.stop() : speechRecognition.start());
} else {
	voiceButton.classList.add("unsupported");
	voiceButton.disabled = true;
	voiceButton.title = "Voice input is not supported by this browser";
	voiceButton.setAttribute("aria-label", "Voice input unavailable");
}
pdfInput.addEventListener("change", () => uploadFile(pdfInput.files[0]));
dropZone.addEventListener("dragover", (event) => { event.preventDefault(); dropZone.classList.add("dragging"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragging"));
dropZone.addEventListener("drop", (event) => { event.preventDefault(); dropZone.classList.remove("dragging"); uploadFile(event.dataTransfer.files[0]); });
document.querySelector("#remove-document").addEventListener("click", clearDocument);
document.querySelector("#remove-attachment").addEventListener("click", clearDocument);
document.querySelector("#new-chat").addEventListener("click", () => { messages.innerHTML = ""; clearDocument(); addMessage("assistant", "New conversation started. Your previous history is still saved in the sidebar.", "Studyroom · just now"); });
document.querySelector("#clear-history").addEventListener("click", async () => {
	if (!window.confirm("Delete all saved questions and answers for this account?")) return;
	await fetch("/api/history", { method: "DELETE" });
	messages.innerHTML = "";
	renderHistory([]);
	addMessage("assistant", "Your saved history has been cleared. Start a new study session whenever you’re ready.", "Studyroom · just now");
});
document.querySelector("#menu-button").addEventListener("click", () => document.querySelector("#sidebar").classList.toggle("open"));
async function boot() {
	const response = await fetch("/api/auth/me");
	const data = await response.json();
	if (data.authenticated) showWorkspace(data.user);
}

boot();
