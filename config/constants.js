// Константы приложения
export const APP_CONFIG = {
    NAME: 'PAX',
    VERSION: '1.0.0',
    MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
    SUPPORTED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
    API_TIMEOUT: 10000,
    NOTIFICATION_DURATION: 5000,
    CHAT_MESSAGE_LIMIT: 1000
};

// Названия экранов
export const SCREENS = {
    LOADING: 'loading',
    RESTRICTED: 'restricted',
    FIND_RIDE: 'findRide',
    RIDE_RESULTS: 'rideResults',
    RIDE_DETAILS: 'rideDetails',
    DRIVER_PROFILE: 'driverProfile',
    PAYMENT_METHOD: 'paymentMethod',
    BANK_SELECTION: 'bankSelection',
    PAYMENT_SUCCESS: 'paymentSuccess',
    USER_PROFILE: 'userProfile',
    MY_RIDES: 'myRides',
    CREATE_RIDE: 'createRide',
    DATE_SELECTION: 'dateSelection',
    TIME_SELECTION: 'timeSelection',
    CREATE_RIDE_SUCCESS: 'createRideSuccess',
    EDIT_PROFILE: 'editProfile',
    UPLOAD_AVATAR: 'uploadAvatar',
    UPLOAD_CAR_PHOTO: 'uploadCarPhoto',
    CHAT_SCREEN: 'chatScreen'
};

// Названия навигации
export const NAV_ITEMS = {
    FIND_RIDE: 'find-ride',
    MY_RIDES: 'my-rides',
    CREATE_RIDE: 'create-ride',
    PROFILE: 'profile'
};

// Цвета приложения
export const COLORS = {
    PRIMARY: '#f65446',
    SECONDARY: '#4e89bf',
    SUCCESS: '#4CAF50',
    ERROR: '#f44336',
    WARNING: '#ff9800',
    INFO: '#2196F3',
    LIGHT_GRAY: '#f8f9fa',
    GRAY: '#5f6368',
    DARK_GRAY: '#202124'
};

// Сообщения об ошибках
export const ERROR_MESSAGES = {
    REQUIRED_FIELD: 'Это поле обязательно для заполнения',
    MIN_LENGTH: (min) => `Минимальная длина ${min} символов`,
    MAX_LENGTH: (max) => `Максимальная длина ${max} символов`,
    INVALID_EMAIL: 'Введите корректный email',
    INVALID_PHONE: 'Введите корректный номер телефона',
    MIN_PRICE: 'Минимальная цена 100 ₽',
    INVALID_DATE: 'Дата не может быть в прошлом',
    FILE_TOO_LARGE: 'Файл слишком большой. Максимальный размер 5MB',
    INVALID_FILE_TYPE: 'Выберите изображение',
    NETWORK_ERROR: 'Нет соединения с сервером. Проверьте интернет',
    SERVER_ERROR: 'Ошибка сервера. Попробуйте позже'
};

// API статусы
export const API_STATUS = {
    SUCCESS: 200,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    SERVER_ERROR: 500
}; 