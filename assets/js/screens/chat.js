import { stateManager } from '../state.js';

class ChatScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        return `
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    ${this.stateManager.getChatMessages().map(message => `
                        <div class="message ${message.sender === 'user' ? 'sent' : 'received'}">
                            <div class="message-content">
                                ${message.text}
                                <div class="message-time">${window.utils.formatTime(message.timestamp)}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="chat-input-container">
                    <textarea class="chat-input" id="chatInput" placeholder="Введите сообщение..." rows="1"></textarea>
                    <button class="send-btn" id="sendMessage" disabled>
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        `;
    }

    setupEventHandlers() {
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendMessage');
        
        // Автоматическое изменение размера поля ввода
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 100) + 'px';
            
            // Активация кнопки отправки
            sendBtn.disabled = !chatInput.value.trim();
        });
        
        // Отправка по Enter
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // Прокрутка к последнему сообщению при загрузке
        setTimeout(() => {
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }, 100);
    }

    sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendMessage');
        const message = chatInput.value.trim();
        
        if (!message) return;
        
        sendBtn.disabled = true;
        
        const chatId = this.stateManager.getState('chat').currentChatId;
        window.api.sendMessage(chatId, message).then(newMessage => {
            this.stateManager.addChatMessage(newMessage);
            chatInput.value = '';
            chatInput.style.height = 'auto';
            sendBtn.disabled = true;
            
            // Прокрутка к последнему сообщению
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Имитация ответа водителя
            setTimeout(() => {
                const driverMessage = {
                    id: Date.now() + 1,
                    text: "Понял, спасибо!",
                    sender: 'driver',
                    timestamp: new Date(),
                    type: 'text'
                };
                this.stateManager.addChatMessage(driverMessage);
                
                // Обновляем экран чата
                const messagesContainer = document.getElementById('chatMessages');
                const messageElement = document.createElement('div');
                messageElement.className = 'message received';
                messageElement.innerHTML = `
                    <div class="message-content">
                        ${driverMessage.text}
                        <div class="message-time">${window.utils.formatTime(driverMessage.timestamp)}</div>
                    </div>
                `;
                messagesContainer.appendChild(messageElement);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 2000);
        }).catch(error => {
            window.utils.handleApiError(error, 'sendMessage');
            sendBtn.disabled = false;
        });
    }
}

export default ChatScreen; 