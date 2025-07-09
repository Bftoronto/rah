import { stateManager } from './state.js';
import { Utils } from './utils.js';
import { API } from './api.js';
import { router, Router } from './router.js';

class App {
    constructor() {
        this.router = null;
        this.initialized = false;
        this.keepAliveInterval = null;
        this.errorRetryCount = 0;
        this.maxRetries = 3;
        this.retryDelay = 2000;
    }

    async init() {
        try {
            // Инициализация Telegram Web App
            this.initTelegramWebApp();
            
            // Инициализация глобальных объектов
            this.initGlobalObjects();
            
            // Инициализация роутера
            this.initRouter();
            
            // Инициализация нижней навигации
            this.initBottomNavigation();
            
            // Инициализация уведомлений
            this.initNotifications();
            
            // Запуск keep-alive механизма
            this.startKeepAlive();
            
            // Загрузка данных пользователя и первый экран
            await this.loadInitialData();
            
            this.initialized = true;
            
        } catch (error) {
            console.error('Ошибка инициализации приложения:', error);
            this.showErrorScreen();
        }
    }

    initTelegramWebApp() {
        if (window.Telegram && window.Telegram.WebApp) {
            const tg = window.Telegram.WebApp;
            tg.expand();
            tg.enableClosingConfirmation();
        } else {
            console.warn('Telegram Web App не найден');
        }
    }

    initGlobalObjects() {
        // Делаем объекты доступными глобально для экранов
        window.utils = Utils;
        window.api = API;
        window.router = this.router;
    }

    initRouter() {
        this.router = router;
        window.router = this.router;
        
        // Добавляем middleware
        this.router.use(Router.authMiddleware);
        this.router.use(Router.loggingMiddleware);
    }

    initBottomNavigation() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Обновляем активное состояние
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                
                // Получаем экран из data-атрибута
                const screenId = item.getAttribute('data-screen');
                this.handleNavigation(screenId);
            });
        });
    }

    async handleNavigation(screenId) {
        switch(screenId) {
            case 'find-ride':
                await this.router.navigate('findRide');
                break;
            case 'my-rides':
                await this.router.navigate('loading', 'Загрузка ваших поездок...');
                try {
                    const rides = await API.getMyRides();
                    await this.router.navigate('myRides', rides);
                } catch (error) {
                    Utils.handleApiError(error, 'getMyRides');
                    await this.router.navigate('findRide');
                }
                break;
            case 'create-ride':
                await this.router.navigate('createRide');
                break;
            case 'profile':
                await this.router.navigate('loading', 'Загрузка профиля...');
                try {
                    const user = await API.getUserData();
                    stateManager.updateUserData(user);
                    await this.router.navigate('profile');
                } catch (error) {
                    Utils.handleApiError(error, 'getUserData');
                    await this.router.navigate('findRide');
                }
                break;
        }
    }

    initNotifications() {
        // Запрос разрешения на уведомления
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    API.subscribeToNotifications().then(result => {
                        if (result.success) {
                            Utils.showNotification('Уведомления', 'Уведомления включены', 'success', 3000);
                        }
                    });
                }
            });
        }
    }

    startKeepAlive() {
        // Keep-alive для предотвращения спин-дауна на Render
        this.keepAliveInterval = setInterval(async () => {
            try {
                const response = await fetch('https://pax-backend-2gng.onrender.com/health', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (response.ok) {
                    console.log('Keep-alive ping successful');
                    this.errorRetryCount = 0; // Сброс счетчика ошибок при успешном ping
                }
            } catch (error) {
                console.warn('Keep-alive ping failed:', error);
                this.errorRetryCount++;
                
                if (this.errorRetryCount >= this.maxRetries) {
                    console.error('Too many keep-alive failures, stopping');
                    this.stopKeepAlive();
                }
            }
        }, 10 * 60 * 1000); // Пинг каждые 10 минут
    }

    stopKeepAlive() {
        if (this.keepAliveInterval) {
            clearInterval(this.keepAliveInterval);
            this.keepAliveInterval = null;
        }
    }

    async loadInitialData() {
        try {
            if (window.Telegram && window.Telegram.WebApp) {
                const tg = window.Telegram.WebApp;
                const telegramInitData = tg.initDataUnsafe;
                console.log('Telegram WebApp data:', telegramInitData);
                
                if (telegramInitData && telegramInitData.user && telegramInitData.user.id) {
                    // Подготавливаем данные для верификации
                    const verificationData = {
                        initData: tg.initData, // Строка с подписью
                        initDataUnsafe: telegramInitData, // Распарсенные данные
                        user: telegramInitData.user,
                        hash: telegramInitData.hash || tg.initData,
                        auth_date: telegramInitData.auth_date || Math.floor(Date.now() / 1000),
                        query_id: telegramInitData.query_id,
                        start_param: telegramInitData.start_param
                    };
                    
                    console.log('Sending verification data:', verificationData);
                    
                    // Передаем данные для верификации с retry логикой
                    const verificationResult = await this.retryWithBackoff(() => 
                        API.verifyTelegramUser(verificationData)
                    );
                    
                    // Пытаемся войти в систему с JWT
                    try {
                        const loginResult = await this.retryWithBackoff(() => 
                            API.login(verificationData)
                        );
                        
                        if (loginResult.success) {
                            // Пользователь успешно авторизован
                            stateManager.updateUserData(loginResult.user);
                            
                            // Проверяем баланс и перенаправляем
                            if (loginResult.user.balance <= 0) {
                                await this.router.navigate('restricted');
                            } else {
                                await this.router.navigate('findRide');
                            }
                        } else {
                            // Пользователь не найден, показываем регистрацию
                            stateManager.setState('registrationData', {
                                telegramData: telegramInitData.user
                            });
                            await this.router.navigate('privacyPolicy');
                        }
                    } catch (error) {
                        console.error('Ошибка авторизации:', error);
                        
                        // В случае ошибки показываем регистрацию
                        stateManager.setState('registrationData', {
                            telegramData: telegramInitData.user
                        });
                        await this.router.navigate('privacyPolicy');
                    }
                } else {
                    // Данные Telegram недоступны, показываем экран входа
                    await this.router.navigate('login');
                }
            } else {
                // Запущено вне Telegram, показываем экран входа
                await this.router.navigate('login');
            }
        } catch (error) {
            console.error('Ошибка загрузки начальных данных:', error);
            
            // Показываем уведомление об ошибке
            Utils.showNotification(
                'Ошибка подключения',
                'Проверьте интернет-соединение и попробуйте снова',
                'error'
            );
            
            // Показываем экран ошибки с возможностью повтора
            this.showErrorScreen();
        }
    }

    async retryWithBackoff(fn, maxRetries = 3, baseDelay = 1000) {
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                return await fn();
            } catch (error) {
                console.warn(`Attempt ${attempt + 1} failed:`, error);
                
                if (attempt === maxRetries - 1) {
                    throw error; // Последняя попытка, пробрасываем ошибку
                }
                
                // Экспоненциальная задержка с jitter
                const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    showErrorScreen() {
        const appContent = document.getElementById('appContent');
        if (appContent) {
            // Безопасное создание HTML для экрана ошибки
            const errorContainer = document.createElement('div');
            errorContainer.className = 'text-center p-20';
            
            const errorIcon = document.createElement('div');
            errorIcon.className = 'mb-20';
            errorIcon.style.fontSize = '48px';
            errorIcon.style.color = '#f44336';
            errorIcon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
            
            const errorTitle = document.createElement('h2');
            errorTitle.className = 'section-title';
            errorTitle.textContent = 'Ошибка загрузки';
            
            const errorMessage = document.createElement('p');
            errorMessage.className = 'mt-10';
            errorMessage.textContent = 'Не удалось загрузить приложение';
            
            const retryButton = document.createElement('button');
            retryButton.className = 'btn btn-primary mt-20';
            retryButton.textContent = 'Попробовать снова';
            retryButton.addEventListener('click', () => {
                location.reload();
            });
            
            errorContainer.appendChild(errorIcon);
            errorContainer.appendChild(errorTitle);
            errorContainer.appendChild(errorMessage);
            errorContainer.appendChild(retryButton);
            
            // Очищаем содержимое и добавляем безопасный HTML
            appContent.innerHTML = '';
            appContent.appendChild(errorContainer);
        }
    }

    // Методы для работы с состоянием
    getState() {
        return stateManager.getState();
    }

    updateState(updates) {
        stateManager.updateState(updates);
    }

    // Методы для работы с API
    async callAPI(method, ...args) {
        return await API[method](...args);
    }

    // Методы для работы с уведомлениями
    showNotification(title, message, type = 'info', duration = 5000) {
        Utils.showNotification(title, message, type, duration);
    }

    // Методы для навигации
    async navigateTo(screenName, data = null) {
        await this.router.navigate(screenName, data);
    }

    async goBack() {
        await this.router.goBack();
    }
}

// Создание и экспорт экземпляра приложения
const app = new App();

// Инициализация приложения при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    app.init();
});

export default app; 