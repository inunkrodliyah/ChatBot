async function sendMessage(){

    let input =
        document.getElementById("user-input");

    let message = input.value;

    if(message === "") return;

    let chatBox =
        document.getElementById("chat-box");

    chatBox.innerHTML +=
    `<div class="user">
        ${message}
    </div>`;

    const response = await fetch('/chat',{
        method:'POST',
        headers:{
            'Content-Type':'application/json'
        },
        body:JSON.stringify({
            message:message
        })
    });

    const data = await response.json();

    chatBox.innerHTML +=
    `<div class="bot">
        ${data.response}
    </div>`;

    input.value = "";

    chatBox.scrollTop =
        chatBox.scrollHeight;
}