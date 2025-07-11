import { stateManager } from './state.js';
import Utils from './utils.js';
import screens, { getAllScreens } from './screens/index.js';

// Импорты для fallback экранов
import FindRideScreen from './screens/findRide.js';
import MyRidesScreen from './screens/myRides.js';
import CreateRideScreen from './screens/createRide.js';
import ProfileScreen from './screens/profile.js';
import RideResultsScreen from './screens/rideResults.js';
import RideDetailsScreen from './screens/rideDetails.js';
import DriverProfileScreen from './screens/driverProfile.js';
import { DateSelectionScreen, TimeSelectionScreen } from './screens/dateTimeSelection.js';
import ChatScreen from './screens/chat.js';
import { UploadAvatarScreen, UploadCarPhotoScreen } from './screens/upload.js';
import EditProfileScreen from './screens/editProfile.js';
import RestrictedScreen from './screens/restricted.js';
import CreateRideSuccessScreen from './screens/success.js';
import NotificationSettingsScreen from './screens/notificationSettings.js';
import RatingScreen from './screens/rating.js';

// Экран загрузки для fallback
class LoadingScreen {
    render(message = "Загрузка...") {
        return `
            <div class="loading-container">
                <div>
                    <div class="loader"></div>
                    <div class="text-center mt-20">${message}</div>
                </div>
            </div>
        `;
    }

    setupEventHandlers() {
        // Нет обработчиков для экрана загрузки
    }
}

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
            const ScreenClass = this.screens.get(screenName);
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
        // Проверяем существование экрана через Map
        if (!this.screens.has(screenName)) {
            console.error(`Экран ${screenName} не найден`);
            return;
        }
        
        // Выполняем middleware
        for (const middleware of this.middlewares) {
            const result = await middleware(screenName, data);
            if (result === false) {
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
                // Безопасная установка HTML с проверкой
                if (typeof html === 'string' && html.trim()) {
                    appContent.innerHTML = html;
                } else {
                    console.warn(`Экран ${screenName} вернул пустой HTML`);
                    appContent.innerHTML = '';
                }
                
                // Устанавливаем обработчики событий
                setTimeout(() => {
                    screenInstance.setupEventHandlers();
                }, 0);
                
            } catch (error) {
                console.error(`Ошибка при рендеринге экрана ${screenName}:`, error);
                
                // Безопасное создание HTML для ошибки
                const errorContainer = document.createElement('div');
                errorContainer.className = 'text-center p-20';
                
                const errorIcon = document.createElement('div');
                errorIcon.className = 'mb-20';
                errorIcon.style.fontSize = '48px';
                errorIcon.style.color = '#f44336';
                errorIcon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
                
                const errorTitle = document.createElement('h2');
                errorTitle.textContent = 'Ошибка';
                
                const errorMessage = document.createElement('p');
                errorMessage.textContent = 'Не удалось загрузить экран';
                
                const backButton = document.createElement('button');
                backButton.className = 'btn btn-primary mt-20';
                backButton.textContent = 'Вернуться к поиску';
                backButton.addEventListener('click', () => {
                    window.router.navigate('findRide');
                });
                
                errorContainer.appendChild(errorIcon);
                errorContainer.appendChild(errorTitle);
                errorContainer.appendChild(errorMessage);
                errorContainer.appendChild(backButton);
                
                // Очищаем содержимое и добавляем безопасный HTML
                appContent.innerHTML = '';
                appContent.appendChild(errorContainer);
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
    async init() {
        try {
            // Получаем все экраны включая регистрацию
            const allScreens = await getAllScreens();
            
            // Регистрируем все экраны
            Object.keys(allScreens).forEach(screenName => {
                this.screens.set(screenName, allScreens[screenName]);
            });
            
            // Настраиваем навигацию по нижнему меню
            this.setupNavigation();
            
            // Загружаем сохраненное состояние
            stateManager.loadFromStorage();
        } catch (error) {
            console.error('Ошибка инициализации роутера:', error);
            // Fallback на базовые экраны - используем только основные экраны
            const basicScreens = {
                findRide: FindRideScreen,
                myRides: MyRidesScreen,
                createRide: CreateRideScreen,
                profile: ProfileScreen,
                rideResults: RideResultsScreen,
                rideDetails: RideDetailsScreen,
                driverProfile: DriverProfileScreen,
                dateSelection: DateSelectionScreen,
                timeSelection: TimeSelectionScreen,
                chatScreen: ChatScreen,
                uploadAvatar: UploadAvatarScreen,
                uploadCarPhoto: UploadCarPhotoScreen,
                editProfile: EditProfileScreen,
                restricted: RestrictedScreen,
                createRideSuccess: CreateRideSuccessScreen,
                notificationSettings: NotificationSettingsScreen,
                rating: RatingScreen,
                loading: LoadingScreen
            };
            
            Object.keys(basicScreens).forEach(screenName => {
                this.screens.set(screenName, basicScreens[screenName]);
            });
        }
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
        return true;
    }
}

// Создаем глобальный экземпляр Router
export const router = new Router();
export { Router };
