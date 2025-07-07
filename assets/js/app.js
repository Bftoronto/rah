import { stateManager } from './state.js';
import { Utils } from './utils.js';
import { API } from './api.js';
import { router } from './router.js';

class App {
    constructor() {
        this.router = null;
        this.initialized = false;
    }

    async init() {
        console.log('Инициализация приложения...');
        
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
            
            // Загрузка данных пользователя и первый экран
            await this.loadInitialData();
            
            this.initialized = true;
            console.log('Приложение успешно инициализировано');
            
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
            console.log('Telegram Web App инициализирован');
        } else {
            console.warn('Telegram Web App не найден');
        }
    }

    initGlobalObjects() {
        // Делаем объекты доступными глобально для экранов
        window.utils = Utils;
        window.api = API;
        window.router = this.router;
        
        console.log('Глобальные объекты инициализированы');
    }

    initRouter() {
        this.router = router;
        window.router = this.router;
        
        // Добавляем middleware
        this.router.use(router.constructor.authMiddleware);
        this.router.use(router.constructor.loggingMiddleware);
        
        console.log('Роутер инициализирован');
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
        
        console.log('Нижняя навигация инициализирована');
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
        
        console.log('Уведомления инициализированы');
    }

    async loadInitialData() {
        console.log('Загрузка начальных данных...');
        
        // Показываем экран загрузки
        await this.router.navigate('loading', 'Загрузка данных...');
        
        try {
            // Проверяем, авторизован ли пользователь через Telegram
            if (window.Telegram && window.Telegram.WebApp) {
                const tg = window.Telegram.WebApp;
                const telegramData = tg.initDataUnsafe?.user;
                
                if (telegramData) {
                    // Верифицируем пользователя через Telegram
                    const verificationResult = await API.verifyTelegramUser(telegramData);
                    
                    if (verificationResult.exists) {
                        // Пользователь существует, загружаем его данные
                        const user = verificationResult.user;
                        stateManager.updateUserData(user);
                        
                        console.log('Пользователь найден:', user);
                        
                        // Определяем начальный экран
                        if (user.balance <= 0) {
                            console.log('Баланс <= 0, показываем экран ограничения');
                            await this.router.navigate('restricted');
                        } else {
                            console.log('Баланс > 0, показываем экран поиска');
                            await this.router.navigate('findRide');
                        }
                    } else {
                        // Пользователь не найден, начинаем регистрацию
                        console.log('Пользователь не найден, начинаем регистрацию');
                        
                        // Сохраняем данные Telegram для регистрации
                        stateManager.setState('registrationData', {
                            telegramData: verificationResult.telegram_data
                        });
                        
                        await this.router.navigate('privacyPolicy');
                    }
                } else {
                    // Нет данных Telegram, показываем экран ограничения
                    console.log('Нет данных Telegram, показываем экран ограничения');
                    await this.router.navigate('restricted');
                }
            } else {
                // Telegram Web App не доступен
                console.log('Telegram Web App не доступен, показываем экран ограничения');
                await this.router.navigate('restricted');
            }
            
        } catch (error) {
            console.error('Ошибка загрузки данных пользователя:', error);
            Utils.handleApiError(error, 'initApp');
            await this.router.navigate('restricted');
        }
    }

    showErrorScreen() {
        const appContent = document.getElementById('appContent');
        if (appContent) {
            appContent.innerHTML = `
                <div class="text-center p-20">
                    <div class="mb-20" style="font-size: 48px; color: #f44336;">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <h2 class="section-title">Ошибка загрузки</h2>
                    <p class="mt-10">Не удалось загрузить приложение</p>
                    <button class="btn btn-primary mt-20" onclick="location.reload()">
                        Попробовать снова
                    </button>
                </div>
            `;
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
    console.log('DOM загружен, начинаю инициализацию приложения');
    app.init();
});

export default app; 