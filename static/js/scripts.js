const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const messagesArea = document.getElementById('messagesArea');

function createMessageElement(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = message;

    messageDiv.appendChild(messageContent);
    return messageDiv;
}

function clearEmptyState() {
    const emptyState = messagesArea.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
}

function scrollToBottom() {
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function addBotResponse(messageArea, bot_response) {
    setTimeout(() => {
        const botMessage = createMessageElement(bot_response, "bot_response");
        messageArea.appendChild(botMessage);

        scrollToBottom(messageArea);

    }, 1000);
}

document.addEventListener('DOMContentLoaded', () => {
    async function handleMessageSubmit(e) {
        e.preventDefault();

        // const message_content = document.querySelector('.input-message');
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const message = messageInput.value.trim();
        if (!message) return;

        // Clear empty state if it exists
        clearEmptyState();

        const responseValue = await fetch("/send_response_to_frontend/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({text: message})
        });

        const dataToBackend = await responseValue.json();

        if (responseValue.ok) {
            // Add user message
            const userMessage = createMessageElement(message, 'user');
            messagesArea.appendChild(userMessage);

            // Clear input
            messageInput.value = '';

            // Scroll to bottom
            scrollToBottom();
            addBotResponse(messagesArea, dataToBackend['bot_answer'])
        }
    }

    messageForm.addEventListener('submit', handleMessageSubmit);
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
