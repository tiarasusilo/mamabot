const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const chatMessages = document.getElementById("chat-messages");
const chatContent = document.getElementById("chat-content");
const chatIntroduction = document.getElementById("chat-introduction");
const sendButton = document.getElementById("send-button");
const suggestionList = document.getElementById("suggestion-list");
const clearButton = document.getElementById("btn-clear");


// Pertanyaan nyata untuk tiap topik di menu beranda (?q=Kehamilan, dst.)
const TOPIK = {
    "kehamilan": "Apa makanan yang baik untuk ibu hamil?",
    "persalinan": "Bagaimana tanda-tanda persalinan?",
    "menyusui": "Bagaimana cara menyusui yang benar?",
    "mpasi": "Kapan bayi mulai diberikan MPASI?",
    "perawatan bayi": "Bagaimana cara memandikan bayi?"
};


// Gulir otomatis ke pesan terbaru
function scrollToBottom() {
    chatContent.scrollTo({ top: chatContent.scrollHeight });
}


// Menyembunyikan sapaan dan saran setelah percakapan dimulai
function hideIntroduction() {
    if (chatIntroduction) {
        chatIntroduction.style.display = "none";
    }
}


// Menampilkan sapaan dan saran lagi (setelah riwayat dihapus)
function showIntroduction() {
    if (chatIntroduction) {
        chatIntroduction.style.display = "";
    }
}


// Menampilkan pesan ke ruang percakapan
function addMessage(sender, message) {
    const messageElement = document.createElement("div");
    messageElement.classList.add("message", sender);

    const label = document.createElement("span");
    label.classList.add("message-label");
    label.textContent = sender === "user" ? "Bunda" : "MamaBot";

    const content = document.createElement("div");
    content.textContent = message;          // textContent: aman dari XSS

    messageElement.appendChild(label);
    messageElement.appendChild(content);

    chatMessages.appendChild(messageElement);
    scrollToBottom();
}


// Indikator "sedang mengetik" selagi menunggu jawaban
function showTyping() {
    const element = document.createElement("div");
    element.classList.add("message", "bot");
    element.id = "typing-indicator";
    element.innerHTML =
        '<span class="message-label">MamaBot</span>' +
        '<span class="typing-dots" aria-label="MamaBot sedang mengetik"><i></i><i></i><i></i></span>';

    chatMessages.appendChild(element);
    scrollToBottom();
}

function hideTyping() {
    const element = document.getElementById("typing-indicator");
    if (element) element.remove();
}


// Mengirim pesan ke Flask
async function sendMessage(message) {
    if (!message.trim()) return;

    hideIntroduction();
    addMessage("user", message);

    messageInput.value = "";
    sendButton.disabled = true;
    sendButton.textContent = "...";
    showTyping();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Terjadi kesalahan.");
        }

        hideTyping();
        addMessage("bot", result.reply);    // kunci dari Flask adalah "reply"

    } catch (error) {
        hideTyping();
        addMessage(
            "bot",
            "Maaf, terjadi kendala saat menghubungkan ke MamaBot. Silakan coba lagi."
        );

        console.error(error);

    } finally {
        sendButton.disabled = false;
        sendButton.textContent = "Kirim";
        messageInput.focus();
    }
}


// Memuat riwayat percakapan sesi ini saat halaman dibuka
async function loadHistory() {
    try {
        const response = await fetch("/api/history");
        if (!response.ok) return;

        const rows = await response.json();
        if (rows.length > 0) {
            hideIntroduction();
            rows.forEach(function (row) {
                addMessage(row.sender, row.text);
            });
        }
    } catch (error) {
        console.error(error);
    }
}


// Ketika formulir dikirim
chatForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const message = messageInput.value.trim();

    sendMessage(message);
});


// Ketika pengguna memilih saran pertanyaan
suggestionList.addEventListener("click", function (event) {
    const button = event.target.closest(".suggestion-button");

    if (button) {
        sendMessage(button.textContent.trim());
    }
});


// Tombol "Hapus riwayat"
if (clearButton) {
    clearButton.addEventListener("click", async function () {
        try {
            await fetch("/api/history", { method: "DELETE" });
        } catch (error) {
            console.error(error);
        }

        chatMessages.innerHTML = "";
        showIntroduction();
        messageInput.focus();
    });
}


// Saat halaman dibuka: muat riwayat dulu, lalu proses ?q= dari beranda (bila ada)
async function init() {
    await loadHistory();

    const q = new URLSearchParams(window.location.search).get("q");

    if (q && q.trim()) {
        const topik = q.trim();
        // Nama topik dipetakan ke pertanyaan nyata; teks lain dikirim apa adanya
        sendMessage(TOPIK[topik.toLowerCase()] || topik);

        // Bersihkan ?q=... dari alamat supaya tidak terkirim lagi saat di-refresh
        window.history.replaceState({}, "", window.location.pathname);
    }
}

init();