import { stateManager } from './state.js';
import { Utils } from './utils.js';
import screens from './screens/index.js';

// Маршрутизатор для навигации между экранами
class Router {
    constructor() {
        this.currentScreen = null;
        this.previousScreen = null;
        this.screenInstances = {};
        this.screens = new Map();
        this.middlewares = [];
    }
    
    // Регистрация экрана
    register(screenName, screenHandler) {
        this.screens.set(screenName, screenHandler);
    }
    
    // Добавление middleware
    use(middleware) {
        this.middlewares.push(middleware);
    }
    
    // Создание экземпляра экрана
    getScreenInstance(screenName) {
        if (!this.screenInstances[screenName]) {
            const ScreenClass = screens[screenName];
            if (ScreenClass) {
                this.screenInstances[screenName] = new ScreenClass();
            } else {
                console.error(`Экран ${screenName} не найден`);
                return null;
            }
        }
        return this.screenInstances[screenName];
    }
    
    // Навигация к экрану
    async navigate(screenName, data = null) {
        console.log(`Router: переход к экрану ${screenName}`, data);
        
        // Проверяем существование экрана через screens объект, а не Map
        if (!screens[screenName]) {
            console.error(`Экран ${screenName} не найден`);
            return;
        }
        
        // Выполняем middleware
        for (const middleware of this.middlewares) {
            const result = await middleware(screenName, data);
            if (result === false) {
                console.log(`Middleware заблокировал переход к ${screenName}`);
                return;
            }
        }
        
        // Сохраняем предыдущий экран
        this.previousScreen = this.currentScreen;
        this.currentScreen = screenName;
        
        // Обновляем состояние
        stateManager.setCurrentScreen(screenName);
        
        // Обновляем заголовок
        this.updateHeader(screenName);
        
        // Получаем экземпляр экрана
        const screenInstance = this.getScreenInstance(screenName);
        if (!screenInstance) {
            console.error(`Не удалось создать экземпляр экрана ${screenName}`);
            return;
        }
        
        // Рендерим экран
        const appContent = document.getElementById('appContent');
        if (appContent) {
            try {
                const html = screenInstance.render(data);
                appContent.innerHTML = html;
                
                // Устанавливаем обработчики событий
                setTimeout(() => {
                    screenInstance.setupEventHandlers();
                }, 0);
                
                console.log(`Экран ${screenName} успешно отрендерен`);
            } catch (error) {
                console.error(`Ошибка при рендеринге экрана ${screenName}:`, error);
                appContent.innerHTML = `
                    <div class="text-center p-20">
                        <h2>Ошибка</h2>
                        <p>Не удалось загрузить экран</p>
                        <button class="btn btn-primary mt-20" onclick="window.router.navigate('findRide')">
                            Вернуться к поиску
                        </button>
                    </div>
                `;
            }
        }
    }
    
    // Обновление заголовка
    updateHeader(screenName) {
        const headerTitle = document.getElementById('headerTitle');
        if (headerTitle) {
            const titles = {
                'restricted': 'PAX',
                'findRide': 'Найти поездку',
                'rideResults': 'Результаты поиска',
                'rideDetails': 'Детали поездки',
                'driverProfile': 'Профиль водителя',
                'paymentMethod': 'Способ оплаты',
                'bankSelection': 'Выбор банка',
                'paymentSuccess': 'Успешная оплата',
                'profile': 'Профиль',
                'myRides': 'Мои поездки',
                'createRide': 'Создать поездку',
                'dateSelection': 'Выбор даты',
                'timeSelection': 'Выбор времени',
                'createRideSuccess': 'Поездка создана',
                'editProfile': 'Редактирование профиля',
                'uploadAvatar': 'Загрузка фото профиля',
                'uploadCarPhoto': 'Фото автомобиля',
                'chatScreen': 'Чат с водителем',
                'notificationSettings': 'Настройки уведомлений',
                'rating': 'Рейтинги и отзывы',
                'createRating': 'Оценить поездку',
                'createReview': 'Оставить отзыв',
                'loading': 'PAX'
            };
            
            headerTitle.textContent = titles[screenName] || 'PAX';
        }
    }
    
    // Получение текущего экрана
    getCurrentScreen() {
        return this.currentScreen;
    }
    
    // Получение предыдущего экрана
    getPreviousScreen() {
        return this.previousScreen;
    }
    
    // Возврат к предыдущему экрану
    goBack() {
        if (this.previousScreen) {
            this.navigate(this.previousScreen);
        } else {
            this.navigate('findRide');
        }
    }
    
    // Инициализация маршрутизатора
    init() {
        console.log('Router: инициализация');
        
        // Регистрируем все экраны напрямую через статический импорт
        Object.keys(screens).forEach(screenName => {
            this.screens.set(screenName, screens[screenName]);
        });
        
        // Настраиваем навигацию по нижнему меню
        this.setupNavigation();
        
        // Загружаем сохраненное состояние
        stateManager.loadFromStorage();
        
        console.log('Router инициализирован');
    }
    
    // Настройка навигации по нижнему меню
    setupNavigation() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', async (event) => {
                event.preventDefault();
                
                const screenId = item.getAttribute('data-screen');
                
                // Обновляем активное состояние
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                
                // Определяем экран для перехода
                let targetScreen = 'findRide';
                
                switch(screenId) {
                    case 'find-ride':
                        targetScreen = 'findRide';
                        break;
                    case 'my-rides':
                        targetScreen = 'myRides';
                        break;
                    case 'create-ride':
                        targetScreen = 'createRide';
                        break;
                    case 'profile':
                        targetScreen = 'profile';
                        break;
                }
                
                // Переходим к экрану
                await this.navigate(targetScreen);
            });
        });
    }
    
    // Middleware для проверки авторизации
    static authMiddleware(screenName, data) {
        const userData = stateManager.getUserData();
        
        // Экраны, требующие положительный баланс
        const restrictedScreens = ['findRide', 'createRide', 'myRides'];
        
        if (restrictedScreens.includes(screenName) && userData.balance <= 0) {
            // Перенаправляем на экран ограничения
            setTimeout(() => {
                window.router.navigate('restricted');
            }, 0);
            return false;
        }
        
        return true;
    }
    
    // Middleware для логирования
    static loggingMiddleware(screenName, data) {
        console.log(`Переход к экрану: ${screenName}`, data);
        return true;
    }
}

// Создаем глобальный экземпляр Router
export const router = new Router();
export { Router };
