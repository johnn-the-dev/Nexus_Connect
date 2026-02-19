document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    
    if (alerts.length > 0) {
        setTimeout(function () {
            alerts.forEach(function (alert) {
                let bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 4000);
    }

    const chatContainer = document.getElementById('conversation');
    
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    const inputs = document.getElementsByTagName('input');
    for (let i = 0; i < inputs.length; i++) {
        if (inputs[i].type !== 'checkbox' && inputs[i].type !== 'radio') {
            inputs[i].classList.add('form-control');
        }
    }

    const selects = document.getElementsByTagName('select');
    for (let i = 0; i < selects.length; i++) {
        selects[i].classList.add('form-select');
    }

    const textareas = document.getElementsByTagName('textarea');
    for (let i = 0; i < textareas.length; i++) {
        textareas[i].classList.add('form-control');
        if (!textareas[i].rows) {
            textareas[i].rows = 5;
        }
    }

    const chatToggleBtn = document.getElementById("chat-toggle-btn");
    const chatWindow = document.getElementById("chat-window");
    const chatCloseBtn = document.getElementById("chat-close-btn");
    const chatInput = document.getElementById("chat-input");
    const chatSendBtn = document.getElementById("chat-send-btn");
    const chatMessages = document.getElementById("chat-messages");
    
    const csrfTokenEl = document.getElementById("chat-csrf-token");
    const csrfToken = csrfTokenEl ? csrfTokenEl.value : '';

    if (chatToggleBtn && chatWindow) {
        chatToggleBtn.addEventListener("click", () => {
            chatWindow.classList.toggle("d-none");
            if (!chatWindow.classList.contains("d-none")) {
                chatInput.focus();
            }
        });

        chatCloseBtn.addEventListener("click", () => {
            chatWindow.classList.add("d-none");
        });

        chatSendBtn.addEventListener("click", sendMessage);
        chatInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter") {
                sendMessage();
            }
        });

        function sendMessage() {
            const text = chatInput.value.trim();
            if (text === "") return;

            appendMessage("user", text);
            chatInput.value = "";

            const typingId = "typing-" + Date.now();
            appendMessage("ai", "Thinking...", typingId);

            fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ message: text })
            })
            .then(response => response.json())
            .then(data => {
                const typingBubble = document.getElementById(typingId);
                if (typingBubble) typingBubble.remove();
                
                if (data.response) {
                    appendMessage("ai", data.response);
                } else if (data.error) {
                    appendMessage("ai", "Error: " + data.error);
                } else {
                    appendMessage("ai", "Sorry, the server didn't return correct data.");
                }
            })
            .catch(error => {
                const typingBubble = document.getElementById(typingId);
                if (typingBubble) typingBubble.remove();
                
                appendMessage("ai", "Error connecting to the server.");
                console.error('AI Chat Error:', error);
            });
        }

        function appendMessage(sender, text, id = null) {
            const msgDiv = document.createElement("div");
            msgDiv.className = sender === "user" ? "chat-msg-user" : "chat-msg-ai";
            if (id) msgDiv.id = id;

            const badgeSpan = document.createElement("span");
            badgeSpan.className = "badge text-wrap text-start fs-6 fw-normal shadow-sm";
            badgeSpan.textContent = text;

            msgDiv.appendChild(badgeSpan);
            chatMessages.appendChild(msgDiv);

            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
});