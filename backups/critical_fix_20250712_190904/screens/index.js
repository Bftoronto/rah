import FindRideScreen from './findRide.js';
import MyRidesScreen from './myRides.js';
import CreateRideScreen from './createRide.js';
import ProfileScreen from './profile.js';
import RideResultsScreen from './rideResults.js';
import RideDetailsScreen from './rideDetails.js';
import DriverProfileScreen from './driverProfile.js';

import { DateSelectionScreen, TimeSelectionScreen } from './dateTimeSelection.js';
import ChatScreen from './chat.js';
import { UploadAvatarScreen, UploadCarPhotoScreen } from './upload.js';
import EditProfileScreen from './editProfile.js';
import RestrictedScreen from './restricted.js';
import CreateRideSuccessScreen from './success.js';
import NotificationSettingsScreen from './notificationSettings.js';
import RatingScreen from './rating.js';

// Экран загрузки
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

// Регистрация всех экранов
const screens = {
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

// Динамический импорт экранов регистрации для избежания циклических зависимостей
async function getRegistrationScreens() {
    try {
        const registrationModule = await import('./registration.js');
        // Проверяем оба варианта экспорта
        const screens = registrationModule.RegistrationScreens || registrationModule.default;
        return {
            privacyPolicy: screens.privacyPolicy,
            basicInfo: screens.basicInfo,
            driverInfo: screens.driverInfo
        };
    } catch (error) {
        console.error('Ошибка загрузки экранов регистрации:', error);
        return {};
    }
}

// Функция для получения всех экранов включая регистрацию
export async function getAllScreens() {
    const registrationScreens = await getRegistrationScreens();
    return { ...screens, ...registrationScreens };
}

// Экспортируем как именованный экспорт вместо default
export { screens as default }; 