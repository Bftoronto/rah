import { stateManager } from '../state.js';

class ChatScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        const chatContainer = document.createElement('div');
        chatContainer.className = 'chat-container';
        
        const messagesContainer = document.createElement('div');
        messagesContainer.className = 'chat-messages';
        messagesContainer.id = 'chatMessages';
        
        // Безопасно создаем сообщения
        this.stateManager.getChatMessages().forEach(message => {
            const messageElement = document.createElement('div');
            messageElement.className = `message ${message.sender === 'user' ? 'sent' : 'received'}`;
            
            const content = document.createElement('div');
            content.className = 'message-content';
            
            const text = document.createElement('div');
            text.textContent = message.text;
            
            const time = document.createElement('div');
            time.className = 'message-time';
            time.textContent = window.utils.formatTime(message.timestamp);
            
            content.appendChild(text);
            content.appendChild(time);
            messageElement.appendChild(content);
            messagesContainer.appendChild(messageElement);
        });
        
        const inputContainer = document.createElement('div');
        inputContainer.className = 'chat-input-container';
        
        const textarea = document.createElement('textarea');
        textarea.className = 'chat-input';
        textarea.id = 'chatInput';
        textarea.placeholder = 'Введите сообщение...';
        textarea.rows = 1;
        
        const sendBtn = document.createElement('button');
        sendBtn.className = 'send-btn';
        sendBtn.id = 'sendMessage';
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        
        inputContainer.appendChild(textarea);
        inputContainer.appendChild(sendBtn);
        
        chatContainer.appendChild(messagesContainer);
        chatContainer.appendChild(inputContainer);
        
        return chatContainer.outerHTML;
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
                
                // Обновляем экран чата безопасно
                const messagesContainer = document.getElementById('chatMessages');
                const messageElement = document.createElement('div');
                messageElement.className = 'message received';
                
                const content = document.createElement('div');
                content.className = 'message-content';
                
                const text = document.createElement('div');
                text.textContent = driverMessage.text;
                
                const time = document.createElement('div');
                time.className = 'message-time';
                time.textContent = window.utils.formatTime(driverMessage.timestamp);
                
                content.appendChild(text);
                content.appendChild(time);
                messageElement.appendChild(content);
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