import { stateManager } from '../state.js';
import { wsManager } from '../websocket.js';
import { API } from '../api.js';
import { Utils } from '../utils.js';

class ChatScreen {
    constructor() {
        this.stateManager = stateManager;
        this.currentChatId = null;
        this.messages = [];
        this.isTyping = false;
        this.typingTimeout = null;
    }

    render() {
        const chatContainer = document.createElement('div');
        chatContainer.className = 'chat-container';
        
        // Статус соединения
        const statusBar = document.createElement('div');
        statusBar.className = 'chat-status-bar';
        statusBar.id = 'chatStatusBar';
        
        const statusIndicator = document.createElement('div');
        statusIndicator.className = 'status-indicator';
        statusIndicator.id = 'statusIndicator';
        
        const statusText = document.createElement('span');
        statusText.id = 'statusText';
        statusText.textContent = 'Подключение...';
        
        statusBar.appendChild(statusIndicator);
        statusBar.appendChild(statusText);
        
        // Контейнер сообщений
        const messagesContainer = document.createElement('div');
        messagesContainer.className = 'chat-messages';
        messagesContainer.id = 'chatMessages';
        
        // Индикатор набора текста
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.id = 'typingIndicator';
        typingIndicator.style.display = 'none';
        typingIndicator.innerHTML = '<span>Печатает...</span>';
        
        // Контейнер ввода
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
        
        // Собираем контейнер
        chatContainer.appendChild(statusBar);
        chatContainer.appendChild(messagesContainer);
        chatContainer.appendChild(typingIndicator);
        chatContainer.appendChild(inputContainer);
        
        return chatContainer.outerHTML;
    }

    setupEventHandlers() {
        this.setupStatusHandlers();
        this.setupInputHandlers();
        this.setupMessageHandlers();
        this.loadMessages();
    }

    setupStatusHandlers() {
        // Обновление статуса соединения
        const updateStatus = (status) => {
            const statusIndicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            
            if (statusIndicator && statusText) {
                switch (status) {
                    case 'connected':
                        statusIndicator.className = 'status-indicator connected';
                        statusText.textContent = 'Подключено';
                        break;
                    case 'disconnected':
                        statusIndicator.className = 'status-indicator disconnected';
                        statusText.textContent = 'Отключено';
                        break;
                    case 'connecting':
                        statusIndicator.className = 'status-indicator connecting';
                        statusText.textContent = 'Подключение...';
                        break;
                    case 'error':
                        statusIndicator.className = 'status-indicator error';
                        statusText.textContent = 'Ошибка соединения';
                        break;
                }
            }
        };

        // Подписываемся на изменения статуса
        wsManager.onStatusChangeCallback = updateStatus;
        updateStatus(wsManager.getStatus());
    }

    setupInputHandlers() {
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendMessage');
        
        if (!chatInput || !sendBtn) return;
        
        // Автоматическое изменение размера поля ввода
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 100) + 'px';
            
            // Активация кнопки отправки
            sendBtn.disabled = !chatInput.value.trim();
            
            // Отправка индикатора набора текста
            this.handleTyping();
        });
        
        // Отправка по Enter
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Отправка по клику
        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });
    }

    setupMessageHandlers() {
        // Подписываемся на входящие сообщения
        wsManager.onMessageCallback = (data) => {
            this.handleIncomingMessage(data);
        };
    }

    async loadMessages() {
        try {
            const chatId = this.stateManager.getState('chat').currentChatId;
            if (!chatId) {
                Utils.showNotification('Ошибка', 'ID чата не найден', 'error');
                return;
            }

            this.currentChatId = chatId;
            
            // Загружаем сообщения через API
            const messages = await API.getChatMessages(chatId);
            this.messages = messages;
            
            this.renderMessages();
            this.scrollToBottom();
            
            // Отмечаем сообщения как прочитанные
            wsManager.markAsRead(chatId);
            
        } catch (error) {
            Utils.handleApiError(error, 'loadMessages');
        }
    }

    renderMessages() {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;
        
        messagesContainer.innerHTML = '';
        
        this.messages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            messagesContainer.appendChild(messageElement);
        });
    }

    createMessageElement(message) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${message.user_from_id === this.stateManager.getCurrentUser().id ? 'sent' : 'received'}`;
        messageElement.setAttribute('data-message-id', message.id);
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const text = document.createElement('div');
        text.className = 'message-text';
        text.textContent = message.message;
        
        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = Utils.formatTime(message.timestamp);
        
        const status = document.createElement('div');
        status.className = 'message-status';
        
        if (message.user_from_id === this.stateManager.getCurrentUser().id) {
            if (message.is_read) {
                status.innerHTML = '<i class="fas fa-check-double"></i>';
            } else {
                status.innerHTML = '<i class="fas fa-check"></i>';
            }
        }
        
        content.appendChild(text);
        content.appendChild(time);
        content.appendChild(status);
        messageElement.appendChild(content);
        
        return messageElement;
    }

    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendMessage');
        const message = chatInput.value.trim();
        
        if (!message || !this.currentChatId) return;
        
        sendBtn.disabled = true;
        
        try {
            // Отправляем через WebSocket
            wsManager.sendMessage(this.currentChatId, message);
            
            // Очищаем поле ввода
            chatInput.value = '';
            chatInput.style.height = 'auto';
            sendBtn.disabled = true;
            
            // Добавляем сообщение в локальный список
            const newMessage = {
                id: Date.now(),
                message: message,
                user_from_id: this.stateManager.getCurrentUser().id,
                user_to_id: null,
                timestamp: new Date(),
                is_read: false
            };
            
            this.messages.push(newMessage);
            this.renderMessages();
            this.scrollToBottom();
            
        } catch (error) {
            Utils.handleApiError(error, 'sendMessage');
            sendBtn.disabled = false;
        }
    }

    handleIncomingMessage(data) {
        switch (data.type) {
            case 'new_message':
                this.handleNewMessage(data.message);
                break;
            case 'message_sent':
                this.handleMessageSent(data);
                break;
            case 'typing':
                this.handleTypingIndicator(data);
                break;
            case 'messages_read':
                this.handleMessagesRead(data);
                break;
        }
    }

    handleNewMessage(message) {
        // Добавляем новое сообщение в список
        this.messages.push(message);
        
        // Обновляем UI
        this.renderMessages();
        this.scrollToBottom();
        
        // Показываем уведомление, если чат не в фокусе
        if (!document.hasFocus()) {
            Utils.showNotification('Новое сообщение', message.message.substring(0, 50) + '...', 'info');
        }
    }

    handleMessageSent(data) {
        // Обновляем статус отправленного сообщения
        const messageElement = document.querySelector(`[data-message-id="${data.message_id}"]`);
        if (messageElement) {
            const statusElement = messageElement.querySelector('.message-status');
            if (statusElement) {
                statusElement.innerHTML = '<i class="fas fa-check"></i>';
            }
        }
    }

    handleTypingIndicator(data) {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            if (data.user_id !== this.stateManager.getCurrentUser().id) {
                typingIndicator.style.display = 'block';
                
                // Скрываем индикатор через 3 секунды
                setTimeout(() => {
                    typingIndicator.style.display = 'none';
                }, 3000);
            }
        }
    }

    handleMessagesRead(data) {
        // Обновляем статус прочтения для всех сообщений от текущего пользователя
        const messageElements = document.querySelectorAll('.message.sent .message-status');
        messageElements.forEach(element => {
            element.innerHTML = '<i class="fas fa-check-double"></i>';
        });
    }

    handleTyping() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        wsManager.sendTyping(this.currentChatId);
        
        // Сбрасываем таймер
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        // Останавливаем индикатор через 1 секунду
        this.typingTimeout = setTimeout(() => {
            this.isTyping = false;
        }, 1000);
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    destroy() {
        // Очищаем таймеры
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
        
        // Отписываемся от WebSocket
        wsManager.onMessageCallback = null;
        wsManager.onStatusChangeCallback = null;
    }
}

export default ChatScreen; 