console.log(" AI Assistant Loaded");

// ================= CONFIG =================
const API_BASE = "http://127.0.0.1:8000";

let isProcessing = false;

// ================= UTIL =================
function getText() {
    return document.getElementById("inputText").value.trim();
}

function setText(val) {
    const el = document.getElementById("inputText");
    el.value = val || "";
    autoResize(el);
}

function autoResize(el) {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

// ================= CHAT MESSAGE =================
function addMessage(text, sender = "bot") {

    const msgArea = document.getElementById("msgArea");

    const wrapper = document.createElement("div");
    wrapper.className = `message ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "bubble";

    // Message Text
    const messageText = document.createElement("p");
    messageText.className = "message-content";
    messageText.innerText = text;
    bubble.appendChild(messageText);

    // Small Copy Icon Button
    const copyBtn = document.createElement("button");
    copyBtn.className = "copy-btn";
    copyBtn.innerHTML = "📋";
    copyBtn.title = "Copy message";

    copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(text).then(() => {
            const original = copyBtn.innerHTML;
            copyBtn.innerHTML = "✅";
            copyBtn.style.color = "#22c55e";

            setTimeout(() => {
                copyBtn.innerHTML = original;
                copyBtn.style.color = "";
            }, 1800);
        });
    });

    bubble.appendChild(copyBtn);

    // Time
    const time = document.createElement("div");
    time.className = "msg-time";
    const now = new Date();
    time.innerText = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    wrapper.appendChild(bubble);
    wrapper.appendChild(time);

    msgArea.appendChild(wrapper);
    msgArea.scrollTo({ top: msgArea.scrollHeight, behavior: "smooth" });
}


// ================= TYPING =================
function showTyping(show) {

    const existing =
        document.getElementById("typingRow");

    if (show) {

        if (existing) return;

        const div =
            document.createElement("div");

        div.className =
            "message bot";

        div.id =
            "typingRow";

        div.innerHTML = `
            <div class="bubble typing-bubble">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;

        document
            .getElementById("msgArea")
            .appendChild(div);

    } else {

        existing?.remove();

    }

    const msgArea =
        document.getElementById("msgArea");

    msgArea.scrollTop =
        msgArea.scrollHeight;
}

// ================= SAFE FETCH =================
async function safeFetch(url, options) {

    if (isProcessing) return null;

    isProcessing = true;

    try {

        const response =
            await fetch(url, options);

        const data =
            await response.json();

        return data;

    } catch (err) {

        addMessage(
            "" + err.message,
            "bot"
        );

        return null;

    } finally {

        isProcessing = false;

    }
}

// ================= GENERATE =================
async function generateText() {

    const text = getText();

    if (!text) {
        addMessage(
            "Enter text first!",
            "bot"
        );
        return;
    }

    addMessage(text, "user");

    showTyping(true);

    const data =
        await safeFetch(
            `${API_BASE}/generate`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    prompt: text
                })
            }
        );

    showTyping(false);

    if (data?.response) {
        addMessage(
            data.response,
            "bot"
        );
    }

    setText("");
}

// ================= SUMMARIZE =================
async function summarizeText() {

    const text = getText();

    if (!text) {
        addMessage(
            "Enter text to summarize!",
            "bot"
        );
        return;
    }

    addMessage(text, "user");

    showTyping(true);

    const data =
        await safeFetch(
            `${API_BASE}/summarize`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    text: text,
                    target_language:
                        "English"
                })
            }
        );

    showTyping(false);

    if (data?.response) {
        addMessage(
            data.response,
            "bot"
        );
    }

    setText("");
}

// ================= TRANSLATE =================
async function translateTo(lang) {

    const text = getText();

    if (!text) {
        addMessage(
            "Enter text to translate!",
            "bot"
        );
        return;
    }

    addMessage(
        `Translate → ${lang}: ${text}`,
        "user"
    );

    showTyping(true);

    const data =
        await safeFetch(
            `${API_BASE}/translate`,
            {
                method: "POST",
                headers: {
                    "Content-Type":
                        "application/json"
                },
                body: JSON.stringify({
                    text: text,
                    target_language: lang
                })
            }
        );

    showTyping(false);

    if (data?.response) {
        addMessage(
            data.response,
            "bot"
        );
    }

    setText("");
}

// ================= OCR =================
async function extractText() {

    const fileInput =
        document.getElementById(
            "fileInput"
        );

    const file =
        fileInput.files[0];

    if (!file) {

        addMessage(
            "Select a file first!",
            "bot"
        );

        return;
    }

    addMessage(
        `+ ${file.name}`,
        "user"
    );

    showTyping(true);

    const form =
        new FormData();

    form.append(
        "file",
        file
    );

    const data =
        await safeFetch(
            `${API_BASE}/extract-text`,
            {
                method: "POST",
                body: form
            }
        );

    showTyping(false);

    if (data?.text) {

        addMessage(
            data.text,
            "bot"
        );

        setText(
            data.text
        );

    } else {

        addMessage(
            "No text found",
            "bot"
        );
    }

    fileInput.value = "";
}

// ================= INIT =================
document.addEventListener(
    "DOMContentLoaded",
    () => {

        const input =
            document.getElementById(
                "inputText"
            );

        const fileInput =
            document.getElementById(
                "fileInput"
            );

        addMessage(
            "👋 Welcome! Upload a file, generate text, summarize content, or translate text.",
            "bot"
        );

        autoResize(input);

        input.addEventListener(
            "input",
            () => autoResize(input)
        );

        // Enter = Send
        input.addEventListener(
            "keydown",
            (e) => {

                if (
                    e.key === "Enter" &&
                    !e.shiftKey
                ) {

                    e.preventDefault();

                    generateText();
                }
            }
        );

        fileInput.addEventListener(
            "change",
            () => {

                if (
                    fileInput.files[0]
                ) {
                    extractText();
                }
            }
        );
    }
);

// ================= CLEAR CHAT =================
function clearChat() {
    console.log("Clear chat button clicked"); // For debugging

    if (confirm("Clear entire chat history?")) {
        const msgArea = document.getElementById("msgArea");
        
        if (msgArea) {
            msgArea.innerHTML = '';
            addMessage("👋 Chat cleared. How can I help you today?", "bot");
        } else {
            console.error("msgArea not found!");
        }
    }
}