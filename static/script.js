async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (message === "") return;

    const chatBox = document.getElementById("chat-box");

    // Menambahkan pesan user ke UI
    chatBox.innerHTML += `
        <div class="message user-message">
            <div class="bubble">${escapeHtml(message)}</div>
        </div>
    `;

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) throw new Error("Gagal mengambil data");

        const data = await response.json();

        // Menambahkan respons bot ke UI
        chatBox.innerHTML += `
            <div class="message bot-message">
                <div class="bubble">${data.response}</div>
            </div>
        `;
    } catch (error) {
        chatBox.innerHTML += `
            <div class="message bot-message">
                <div class="bubble" style="color: red;">Terjadi masalah jaringan atau server belum siap.</div>
            </div>
        `;
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});