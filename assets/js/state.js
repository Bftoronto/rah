// Управление состоянием приложения
export class StateManager {
    constructor() {
        this.state = {
            currentScreen: 'loading',
            previousScreen: null,
            userData: {
                id: 123456,
                name: "Александр Горин",
                balance: 500,
                rating: 5.0,
                reviews: 123,
                avatar: null,
                car: {
                    model: "LADA Granta",
                    year: 2023,
                    color: "Серый",
                    plate: "A 123 AA",
                    photo: null
                },
                verified: {
                    passport: true,
                    phone: true,
                    car: true
                },
                cancelledRides: 0
            },
            rides: [],
            paymentAmount: 500,
            selectedDate: null,
            selectedTime: null,
            selectedRide: null,
            newRide: {
                from: "",
                to: "",
                stops: [],
                date: "",
                time: "",
                passengers: 3,
                price: 500
            },
            // Чат
            chat: {
                messages: [],
                currentChatId: null,
                isTyping: false
            },
            // Изображения
            images: {
                userAvatar: null,
                carPhoto: null,
                passportPhoto: null
            },
            // Уведомления
            notifications: [],
            selectedCalendarMonth: undefined,
            selectedCalendarYear: undefined,
            _calendarRangeMode: null,
            selectedDateFrom: null,
            selectedDateTo: null,
            // Флаги для баннеров
            hideMyRidesInfoBanner: false,
            hideCreateInfoBanner: false
        };
        
        this.listeners = new Map();
    }
    
    // Подписка на изменения состояния
    subscribe(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, []);
        }
        this.listeners.get(key).push(callback);
        
        // Возвращаем функцию для отписки
        return () => {
            const callbacks = this.listeners.get(key);
            if (callbacks) {
                const index = callbacks.indexOf(callback);
                if (index > -1) {
                    callbacks.splice(index, 1);
                }
            }
        };
    }
    
    // Установка значения состояния
    setState(key, value) {
        this.state[key] = value;
        this.notify(key, value);
    }
    
    // Получение значения состояния
    getState(key) {
        return this.state[key];
    }
    
    // Обновление части состояния
    updateState(updates) {
        Object.assign(this.state, updates);
        
        // Уведомляем всех подписчиков об изменениях
        Object.keys(updates).forEach(key => {
            this.notify(key, updates[key]);
        });
    }
    
    // Уведомление подписчиков
    notify(key, value) {
        const callbacks = this.listeners.get(key);
        if (callbacks) {
            callbacks.forEach(callback => {
                try {
                    callback(value, this.state);
                } catch (error) {
                    console.error('Error in state listener:', error);
                }
            });
        }
    }
    
    // Получение всего состояния
    getFullState() {
        return { ...this.state };
    }
    
    // Сброс состояния к начальным значениям
    reset() {
        this.state = {
            currentScreen: 'loading',
            previousScreen: null,
            userData: {
                id: 123456,
                name: "Александр Горин",
                balance: 500,
                rating: 5.0,
                reviews: 123,
                avatar: null,
                car: {
                    model: "LADA Granta",
                    year: 2023,
                    color: "Серый",
                    plate: "A 123 AA",
                    photo: null
                },
                verified: {
                    passport: true,
                    phone: true,
                    car: true
                },
                cancelledRides: 0
            },
            rides: [],
            paymentAmount: 500,
            selectedDate: null,
            selectedTime: null,
            selectedRide: null,
            newRide: {
                from: "",
                to: "",
                stops: [],
                date: "",
                time: "",
                passengers: 3,
                price: 500
            },
            chat: {
                messages: [],
                currentChatId: null,
                isTyping: false
            },
            images: {
                userAvatar: null,
                carPhoto: null,
                passportPhoto: null
            },
            notifications: [],
            selectedCalendarMonth: undefined,
            selectedCalendarYear: undefined,
            _calendarRangeMode: null,
            selectedDateFrom: null,
            selectedDateTo: null,
            hideMyRidesInfoBanner: false,
            hideCreateInfoBanner: false
        };
        
        // Уведомляем всех подписчиков о сбросе
        this.listeners.forEach((callbacks, key) => {
            callbacks.forEach(callback => {
                try {
                    callback(this.state[key], this.state);
                } catch (error) {
                    console.error('Error in state reset listener:', error);
                }
            });
        });
    }
    
    // Сохранение состояния в localStorage с валидацией
    saveToStorage() {
        try {
            // Проверяем размер данных перед сохранением
            const stateString = JSON.stringify(this.state);
            if (stateString.length > 1024 * 1024) { // 1MB лимит
                console.warn('State too large, truncating...');
                // Удаляем большие объекты
                const truncatedState = { ...this.state };
                delete truncatedState.images;
                delete truncatedState.chat;
                localStorage.setItem('pax-app-state', JSON.stringify(truncatedState));
            } else {
                localStorage.setItem('pax-app-state', stateString);
            }
        } catch (error) {
            console.error('Error saving state to storage:', error);
        }
    }
    
    // Загрузка состояния из localStorage с валидацией
    loadFromStorage() {
        try {
            const savedState = localStorage.getItem('pax-app-state');
            if (savedState) {
                const parsedState = JSON.parse(savedState);
                
                // Валидация загруженных данных
                if (parsedState && typeof parsedState === 'object') {
                    this.updateState(parsedState);
                } else {
                    console.warn('Invalid state data in storage, using defaults');
                }
            }
        } catch (error) {
            console.error('Error loading state from storage:', error);
            // Очищаем поврежденные данные
            localStorage.removeItem('pax-app-state');
        }
    }
    
    // Методы для работы с конкретными частями состояния
    
    // Работа с экранами
    setCurrentScreen(screen) {
        this.setState('previousScreen', this.state.currentScreen);
        this.setState('currentScreen', screen);
    }
    
    getCurrentScreen() {
        return this.state.currentScreen;
    }
    
    getPreviousScreen() {
        return this.state.previousScreen;
    }
    
    // Работа с пользователем
    updateUserData(userData) {
        this.setState('userData', { ...this.state.userData, ...userData });
    }
    
    getUserData() {
        return this.state.userData;
    }
    
    // Работа с поездками
    setRides(rides) {
        this.setState('rides', rides);
    }
    
    getRides() {
        return this.state.rides;
    }
    
    setSelectedRide(ride) {
        this.setState('selectedRide', ride);
    }
    
    getSelectedRide() {
        return this.state.selectedRide;
    }
    
    // Работа с датами
    setSelectedDate(date) {
        this.setState('selectedDate', date);
    }
    
    getSelectedDate() {
        return this.state.selectedDate;
    }
    
    setSelectedTime(time) {
        this.setState('selectedTime', time);
    }
    
    getSelectedTime() {
        return this.state.selectedTime;
    }
    
    // Работа с чатом
    setChatMessages(messages) {
        this.setState('chat', { ...this.state.chat, messages });
    }
    
    addChatMessage(message) {
        const messages = [...this.state.chat.messages, message];
        this.setState('chat', { ...this.state.chat, messages });
    }
    
    getChatMessages() {
        return this.state.chat.messages;
    }
    
    // Работа с изображениями
    setUserAvatar(avatar) {
        this.setState('images', { ...this.state.images, userAvatar: avatar });
    }
    
    setCarPhoto(photo) {
        this.setState('images', { ...this.state.images, carPhoto: photo });
    }
    
    // Работа с уведомлениями
    addNotification(notification) {
        const notifications = [...this.state.notifications, notification];
        this.setState('notifications', notifications);
    }
    
    removeNotification(id) {
        const notifications = this.state.notifications.filter(n => n.id !== id);
        this.setState('notifications', notifications);
    }
    
    getNotifications() {
        return this.state.notifications;
    }
}

// Создаем глобальный экземпляр StateManager
export const stateManager = new StateManager(); 