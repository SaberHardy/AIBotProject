document.addEventListener('DOMContentLoaded', () => {
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

    messageForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const message = messageInput.value.trim();
        if (!message) return;

        // Clear empty state if it exists
        clearEmptyState();

        // Add user message
        const userMessage = createMessageElement(message, 'user');
        messagesArea.appendChild(userMessage);

        // Clear input
        messageInput.value = '';

        // Scroll to bottom
        scrollToBottom();
    });
});