async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();

    if (message === "") return;

    const chatBox = document.getElementById("chat-box");

    // 1. Tambahkan pesan user ke UI
    chatBox.innerHTML += `
        <div class="message user-message">
            <div class="bubble">${escapeHtml(message)}</div>
        </div>
    `;

    // Reset input dan scroll otomatis ke bawah
    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // 2. Kirim data ke backend Flask
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) throw new Error("Gagal mengambil data dari server");

        const data = await response.json();

        // 3. Tambahkan respons bot ke UI
        chatBox.innerHTML += `
            <div class="message bot-message">
                <div class="bubble">${data.response}</div>
            </div>
        `;
    } catch (error) {
        chatBox.innerHTML += `
            <div class="message bot-message">
                <div class="bubble" style="color: red;">Terjadi masalah jaringan atau server Sastrawi belum siap.</div>
            </div>
        `;
    }

    // Scroll akhir setelah bot merespons
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Menghindari celah XSS dari input user langsung ke HTML innerHTML
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Deteksi tombol 'Enter' pada input teks agar bisa langsung terkirim
document.getElementById("user-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
});