document.addEventListener('DOMContentLoaded', () => {
    const chatHistory = document.getElementById('chatHistory');
    const userInput = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const modelSelect = document.getElementById('modelSelect');

    // Load chat history from localStorage
    loadChatHistory();

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = userInput.value.trim();
        const model = modelSelect.value;
        
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        userInput.value = '';

        try {
            const response = await fetch('http://localhost:5000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    model
                })
            });

            const data = await response.json();
            addMessage(data.response, 'bot');
        } catch (error) {
            addMessage('Error connecting to the server', 'bot');
        }

        saveChatHistory();
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        messageDiv.textContent = text;
        chatHistory.appendChild(messageDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function saveChatHistory() {
        const messages = Array.from(chatHistory.children).map(el => ({
            text: el.textContent,
            type: el.classList.contains('user-message') ? 'user' : 'bot'
        }));
        localStorage.setItem('chatHistory', JSON.stringify(messages));
    }

    function loadChatHistory() {
        const history = JSON.parse(localStorage.getItem('chatHistory')) || [];
        history.forEach(msg => addMessage(msg.text, msg.type));
    }
});