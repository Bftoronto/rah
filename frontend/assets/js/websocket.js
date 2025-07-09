import { API } from './api.js';
import { Utils } from './utils.js';

// Класс для управления WebSocket соединениями
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.heartbeatInterval = null;
        this.messageQueue = [];
        this.isConnected = false;
        this.userId = null;
        this.onMessageCallback = null;
        this.onStatusChangeCallback = null;
    }

    // Подключение к WebSocket
    connect(userId, onMessage = null, onStatusChange = null) {
        this.userId = userId;
        this.onMessageCallback = onMessage;
        this.onStatusChangeCallback = onStatusChange;

        const wsUrl = this.getWebSocketUrl();
        
        try {
            this.ws = new WebSocket(wsUrl);
            this.setupEventHandlers();
        } catch (error) {
            console.error('Ошибка создания WebSocket соединения:', error);
            this.handleConnectionError(error);
        }
    }

    // Получение WebSocket URL
    getWebSocketUrl() {
        const baseURL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'ws://localhost:8000'
            : 'wss://pax-backend-2gng.onrender.com';
        
        return `${baseURL}/api/chat/ws/${this.userId}`;
    }

    // Настройка обработчиков событий
    setupEventHandlers() {
        this.ws.onopen = () => {
            console.log('WebSocket соединение установлено');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.startHeartbeat();
            this.processMessageQueue();
            
            if (this.onStatusChangeCallback) {
                this.onStatusChangeCallback('connected');
            }
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Ошибка парсинга WebSocket сообщения:', error);
            }
        };

        this.ws.onclose = (event) => {
            console.log('WebSocket соединение закрыто:', event.code, event.reason);
            this.isConnected = false;
            this.stopHeartbeat();
            
            if (this.onStatusChangeCallback) {
                this.onStatusChangeCallback('disconnected');
            }

            // Попытка переподключения
            if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.scheduleReconnect();
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket ошибка:', error);
            this.handleConnectionError(error);
        };
    }

    // Обработка входящих сообщений
    handleMessage(data) {
        switch (data.type) {
            case 'new_message':
                this.handleNewMessage(data);
                break;
            case 'message_sent':
                this.handleMessageSent(data);
                break;
            case 'typing':
                this.handleTyping(data);
                break;
            case 'messages_read':
                this.handleMessagesRead(data);
                break;
            case 'error':
                this.handleError(data);
                break;
            case 'pong':
                // Ответ на heartbeat
                break;
            default:
                console.log('Неизвестный тип сообщения:', data);
        }

        if (this.onMessageCallback) {
            this.onMessageCallback(data);
        }
    }

    // Обработка нового сообщения
    handleNewMessage(data) {
        console.log('Новое сообщение:', data);
        // Здесь можно добавить логику для обновления UI
    }

    // Обработка подтверждения отправки
    handleMessageSent(data) {
        console.log('Сообщение отправлено:', data);
        // Здесь можно добавить логику для обновления UI
    }

    // Обработка индикатора набора текста
    handleTyping(data) {
        console.log('Пользователь набирает текст:', data);
        // Здесь можно добавить логику для отображения индикатора
    }

    // Обработка отметки о прочтении
    handleMessagesRead(data) {
        console.log('Сообщения прочитаны:', data);
        // Здесь можно добавить логику для обновления UI
    }

    // Обработка ошибок
    handleError(data) {
        console.error('WebSocket ошибка:', data);
        Utils.showNotification('Ошибка чата', data.message || 'Произошла ошибка в чате', 'error');
    }

    // Отправка сообщения
    sendMessage(chatId, message) {
        const messageData = {
            type: 'message',
            chat_id: chatId,
            message: message
        };

        this.send(messageData);
    }

    // Отправка данных через WebSocket
    send(data) {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            // Добавляем в очередь, если соединение не установлено
            this.messageQueue.push(data);
        }
    }

    // Обработка очереди сообщений
    processMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.send(message);
        }
    }

    // Отправка индикатора набора текста
    sendTyping(chatId) {
        const typingData = {
            type: 'typing',
            chat_id: chatId
        };

        this.send(typingData);
    }

    // Отметка сообщений как прочитанные
    markAsRead(chatId) {
        const readData = {
            type: 'read',
            chat_id: chatId
        };

        this.send(readData);
    }

    // Heartbeat для поддержания соединения
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'ping' });
            }
        }, 30000); // Каждые 30 секунд
    }

    // Остановка heartbeat
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    // Планирование переподключения
    scheduleReconnect() {
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`Попытка переподключения ${this.reconnectAttempts} через ${delay}ms`);
        
        setTimeout(() => {
            if (!this.isConnected) {
                this.connect(this.userId, this.onMessageCallback, this.onStatusChangeCallback);
            }
        }, delay);
    }

    // Обработка ошибок соединения
    handleConnectionError(error) {
        console.error('Ошибка WebSocket соединения:', error);
        
        if (this.onStatusChangeCallback) {
            this.onStatusChangeCallback('error');
        }
    }

    // Отключение
    disconnect() {
        this.isConnected = false;
        this.stopHeartbeat();
        
        if (this.ws) {
            this.ws.close(1000, 'Пользователь отключился');
            this.ws = null;
        }
    }

    // Получение статуса соединения
    getStatus() {
        if (!this.ws) return 'disconnected';
        
        switch (this.ws.readyState) {
            case WebSocket.CONNECTING:
                return 'connecting';
            case WebSocket.OPEN:
                return 'connected';
            case WebSocket.CLOSING:
                return 'closing';
            case WebSocket.CLOSED:
                return 'disconnected';
            default:
                return 'unknown';
        }
    }

    // Проверка соединения
    isConnectionActive() {
        return this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// Глобальный экземпляр WebSocket менеджера
const wsManager = new WebSocketManager();

// Экспорт для использования в других модулях
export { WebSocketManager, wsManager };

// Автоматическое подключение при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Проверяем, есть ли авторизованный пользователь
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    if (currentUser && currentUser.id) {
        wsManager.connect(currentUser.id, 
            (message) => {
                // Обработка входящих сообщений
                console.log('Получено сообщение:', message);
            },
            (status) => {
                // Обработка изменений статуса
                console.log('Статус WebSocket:', status);
                
                if (status === 'connected') {
                    Utils.showNotification('Чат активен', 'Соединение с чатом установлено', 'success');
                } else if (status === 'disconnected') {
                    Utils.showNotification('Чат неактивен', 'Соединение с чатом потеряно', 'warning');
                }
            }
        );
    }
});

// Обработка отключения при закрытии страницы
window.addEventListener('beforeunload', () => {
    wsManager.disconnect();
}); 