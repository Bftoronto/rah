import Utils from './utils.js';

// JWT Token Management
let accessToken = null;
let refreshToken = null;
let currentUser = null;

// Функция для установки токенов авторизации
function setAuthTokens(tokens) {
    if (tokens.access_token) {
        accessToken = tokens.access_token;
        localStorage.setItem('accessToken', tokens.access_token);
    }
    if (tokens.refresh_token) {
        refreshToken = tokens.refresh_token;
        localStorage.setItem('refreshToken', tokens.refresh_token);
    }
}

// Функция для получения access токена
function getAccessToken() {
    if (!accessToken) {
        accessToken = localStorage.getItem('accessToken');
    }
    return accessToken;
}

// Функция для получения refresh токена
function getRefreshToken() {
    if (!refreshToken) {
        refreshToken = localStorage.getItem('refreshToken');
    }
    return refreshToken;
}

// Функция для очистки токенов авторизации
function clearAuthTokens() {
    accessToken = null;
    refreshToken = null;
    currentUser = null;
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('currentUser');
}

// Функция для обновления токенов
async function refreshAuthTokens() {
    try {
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await fetch(`${currentConfig.baseURL}/api/auth/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh_token: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.tokens) {
                setAuthTokens(data.tokens);
                return true;
            }
        }
        clearAuthTokens();
        return false;
    } catch (error) {
        console.error('Error refreshing tokens:', error);
        clearAuthTokens();
        return false;
    }
}

// Конфигурация API
const API_CONFIG = {
    // Локальная разработка
    development: {
        baseURL: 'http://localhost:8000',
        timeout: 10000
    },
    // Локальная разработка с бэкендом
    local: {
        baseURL: 'http://localhost:8000',
        timeout: 10000
    },
    // Продакшен (Render)
    production: {
        baseURL: 'https://pax-backend-2gng.onrender.com',
        timeout: 15000
    },
    // Telegram Mini App
    telegram: {
        baseURL: 'https://pax-backend-2gng.onrender.com',
        timeout: 10000
    }
};

// Определение окружения
const getEnvironment = () => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'local';
    } else if (window.location.hostname === 'frabjous-florentine-c506b0.netlify.app') {
        return 'production';
    } else if (window.Telegram && window.Telegram.WebApp) {
        return 'telegram';
    }
    return 'production';
};

const currentConfig = API_CONFIG[getEnvironment()];

// Класс для обработки ошибок API
class ApiError extends Error {
    constructor(status, message, data = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
        this.timestamp = new Date();
    }
}

// Класс для кэширования
class CacheManager {
    constructor() {
        this.cache = new Map();
        this.defaultTTL = 5 * 60 * 1000; // 5 минут
        this.cleanupInterval = setInterval(() => this.cleanup(), 60000); // Очистка каждую минуту
    }

    get(key) {
        const item = this.cache.get(key);
        if (item && Date.now() < item.expiresAt) {
            return item.data;
        }
        if (item) {
            this.cache.delete(key);
        }
        return null;
    }

    set(key, data, customTtl = null) {
        const ttl = customTtl || this.defaultTTL;
        this.cache.set(key, {
            data: data,
            expiresAt: Date.now() + ttl,
            createdAt: Date.now()
        });
    }

    clear() {
        this.cache.clear();
    }

    invalidate(pattern) {
        for (const [key] of this.cache) {
            if (key.includes(pattern)) {
                this.cache.delete(key);
            }
        }
    }

    getStats() {
        const now = Date.now();
        let total = 0;
        let expired = 0;
        let active = 0;

        for (const [key, item] of this.cache) {
            total++;
            if (now >= item.expiresAt) {
                expired++;
            } else {
                active++;
            }
        }

        return {
            total,
            expired,
            active,
            size: this.cache.size
        };
    }

    cleanup() {
        const now = Date.now();
        for (const [key, item] of this.cache) {
            if (now >= item.expiresAt) {
                this.cache.delete(key);
            }
        }
    }

    setTTL(key, ttl) {
        const item = this.cache.get(key);
        if (item) {
            item.expiresAt = Date.now() + ttl;
        }
    }

    // Новые методы для синхронизации с бэкендом
    async syncWithBackend() {
        try {
            const response = await API.request('/api/cache/stats', { method: 'GET' });
            if (response.success) {
                console.log('Кэш синхронизирован с бэкендом:', response.data);
                return response.data;
            }
        } catch (error) {
            console.error('Ошибка синхронизации кэша:', error);
        }
        return null;
    }

    async invalidateBackend(pattern = null) {
        try {
            const body = pattern ? { pattern } : {};
            const response = await API.request('/api/cache/invalidate', {
                method: 'POST',
                body: JSON.stringify(body)
            });
            if (response.success) {
                console.log('Кэш бэкенда инвалидирован');
                // Также инвалидируем локальный кэш
                this.invalidate(pattern);
            }
        } catch (error) {
            console.error('Ошибка инвалидации кэша бэкенда:', error);
        }
    }

    async clearBackend() {
        try {
            const response = await API.request('/api/cache/clear', { method: 'DELETE' });
            if (response.success) {
                console.log('Кэш бэкенда очищен');
                // Также очищаем локальный кэш
                this.clear();
            }
        } catch (error) {
            console.error('Ошибка очистки кэша бэкенда:', error);
        }
    }

    // Метод для синхронизации при изменении данных
    async syncOnDataChange(operation, endpoint) {
        try {
            // Инвалидируем связанные кэши
            const patterns = this.getInvalidationPatterns(operation, endpoint);
            for (const pattern of patterns) {
                await this.invalidateBackend(pattern);
            }
        } catch (error) {
            console.error('Ошибка синхронизации кэша при изменении данных:', error);
        }
    }

    // Определение паттернов инвалидации для разных операций
    getInvalidationPatterns(operation, endpoint) {
        const patterns = [];
        
        switch (operation) {
            case 'CREATE':
            case 'UPDATE':
            case 'DELETE':
                if (endpoint.includes('/rides')) {
                    patterns.push('rides', 'my_rides');
                }
                if (endpoint.includes('/profile')) {
                    patterns.push('user_data');
                }
                if (endpoint.includes('/rating')) {
                    patterns.push('ratings', 'reviews');
                }
                if (endpoint.includes('/upload')) {
                    patterns.push('user_data');
                }
                break;
        }
        
        return patterns;
    }
}

// Глобальный экземпляр кэша
const cacheManager = new CacheManager();

// API клиент для работы с сервером
export const API = {
    // Общий метод для запросов с JWT авторизацией
    async request(endpoint, options = {}) {
        const url = `${currentConfig.baseURL}${endpoint}`;
        
        // Определяем, нужно ли устанавливать Content-Type
        const isFormData = options.body instanceof FormData;
        const headers = isFormData ? {} : { 'Content-Type': 'application/json' };
        
        // Добавляем JWT токен если доступен
        const token = getAccessToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const config = {
            headers: {
                ...headers,
                ...options.headers
            },
            ...options
        };
        
        try {
            const startTime = Date.now();
            const response = await fetch(url, config);
            
            // Мониторинг API вызовов
            if (window.performanceMonitor) {
                window.performanceMonitor.trackApiCall(endpoint, options.method || 'GET', startTime);
            }
            
            // Если получили 401, пытаемся обновить токен
            if (response.status === 401) {
                const refreshed = await refreshAuthTokens();
                if (refreshed) {
                    // Повторяем запрос с новым токеном
                    const newToken = getAccessToken();
                    if (newToken) {
                        config.headers['Authorization'] = `Bearer ${newToken}`;
                        const retryResponse = await fetch(url, config);
                        
                        if (retryResponse.ok) {
                            return await retryResponse.json();
                        }
                    }
                }
                
                // Если не удалось обновить токен, очищаем авторизацию
                clearAuthTokens();
                throw new ApiError(401, 'Требуется авторизация');
            }
            
            // Обработка других ошибок
            if (!response.ok) {
                let errorData = null;
                try {
                    errorData = await response.json();
                } catch {
                    errorData = { detail: 'Неизвестная ошибка' };
                }
                
                throw new ApiError(response.status, errorData.detail || 'Ошибка запроса', errorData);
            }
            
            // Успешный ответ
            const data = await response.json();
            
            // Кэшируем успешные GET запросы
            if (options.method === 'GET' || !options.method) {
                const cacheKey = `${options.method || 'GET'}_${endpoint}`;
                cacheManager.set(cacheKey, data);
            }
            
            return data;
            
        } catch (error) {
            if (error instanceof ApiError) {
                throw error;
            }
            
            // Сетевые ошибки
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new ApiError(0, 'Нет соединения с сервером');
            }
            
            throw new ApiError(500, 'Неизвестная ошибка', error);
        }
    },

    // Логирование ошибок для мониторинга
    logError(error, context = '') {
        const errorLog = {
            timestamp: new Date().toISOString(),
            error: error.message,
            status: error.status,
            data: error.data,
            context,
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        // Обработка структурированных ошибок от бекенда
        if (error.data && typeof error.data === 'object' && error.data.success === false) {
            const apiError = error.data;
            errorLog.apiError = {
                code: apiError.error_code,
                message: apiError.message,
                requestId: apiError.request_id,
                details: apiError.error_details,
                timestamp: apiError.timestamp
            };
        }
        
        // Интеграция с системой мониторинга
        if (window.performanceMonitor) {
            window.performanceMonitor.trackError(error, context);
        }
        
        // В продакшене отправляем в систему мониторинга
        if (getEnvironment() === 'production') {
            console.error('Production error:', errorLog);
        } else {
            console.error('Development error:', errorLog);
        }
    },
    
    // Получение данных пользователя
    async getUserData() {
        const cacheKey = 'user_data';
        const cached = cacheManager.get(cacheKey);
        if (cached) return cached;
        
        const data = await this.request('/api/profile', { method: 'GET' });
        cacheManager.set(cacheKey, data);
        return data;
    },
    
    // Поиск поездок (ИСПРАВЛЕНО)
    async getRides(from, to, date, filters = {}) {
        try {
            const params = new URLSearchParams();
            
            // Базовые параметры поиска
            if (from) params.append('from_location', from);
            if (to) params.append('to_location', to);
            if (date) {
                const dateFrom = new Date(date);
                const dateTo = new Date(date);
                dateTo.setDate(dateTo.getDate() + 1);
                params.append('date_from', dateFrom.toISOString());
                params.append('date_to', dateTo.toISOString());
            }
            
            // Дополнительные фильтры
            if (filters.max_price) params.append('max_price', filters.max_price.toString());
            if (filters.min_seats) params.append('min_seats', filters.min_seats.toString());
            if (filters.driver_id) params.append('driver_id', filters.driver_id.toString());
            if (filters.status) params.append('status', filters.status);
            if (filters.limit) params.append('limit', filters.limit.toString());
            if (filters.offset) params.append('offset', filters.offset.toString());
            
            return await this.request(`/api/rides/search?${params.toString()}`, {
                method: 'GET'
            });
        } catch (error) {
            this.logError(error, 'getRides');
            throw error;
        }
    },
    
    // Расширенный поиск поездок с полными фильтрами
    async searchRidesAdvanced(filters = {}) {
        try {
            const params = new URLSearchParams();
            
            // Все доступные параметры фильтрации
            if (filters.from_location) params.append('from_location', filters.from_location);
            if (filters.to_location) params.append('to_location', filters.to_location);
            if (filters.date_from) params.append('date_from', filters.date_from);
            if (filters.date_to) params.append('date_to', filters.date_to);
            if (filters.max_price) params.append('max_price', filters.max_price.toString());
            if (filters.min_seats) params.append('min_seats', filters.min_seats.toString());
            if (filters.driver_id) params.append('driver_id', filters.driver_id.toString());
            if (filters.status) params.append('status', filters.status);
            if (filters.limit) params.append('limit', filters.limit.toString());
            if (filters.offset) params.append('offset', filters.offset.toString());
            
            return await this.request(`/api/rides/search?${params.toString()}`, {
                method: 'GET'
            });
        } catch (error) {
            this.logError(error, 'searchRidesAdvanced');
            throw error;
        }
    },
    
    // Бронирование поездки (ИСПРАВЛЕНО)
    async bookRide(rideId) {
        return this.request(`/api/rides/${rideId}/book`, { method: 'POST' });
    },
    
    // Создание поездки
    async createRide(rideData) {
        const data = await this.request('/api/rides', { method: 'POST', body: JSON.stringify(rideData) });
        // Синхронизируем кэш при создании поездки
        await cacheManager.syncOnDataChange('CREATE', '/api/rides');
        return data;
    },
    
    // Получение детальной информации о поездке
    async getRideDetails(rideId) {
        const cacheKey = `ride_${rideId}`;
        const cached = cacheManager.get(cacheKey);
        if (cached) return cached;
        
        const data = await this.request(`/api/rides/${rideId}`, { method: 'GET' });
        cacheManager.set(cacheKey, data);
        return data;
    },
    
    // Получение моих поездок
    async getMyRides() {
        const cacheKey = 'my_rides';
        const cached = cacheManager.get(cacheKey);
        if (cached) return cached;
        
        const data = await this.request('/api/rides/user/me', { method: 'GET' });
        cacheManager.set(cacheKey, data);
        return data;
    },
    
    // Получение сообщений чата
    async getChatMessages(chatId, limit = 50, offset = 0) {
        const params = new URLSearchParams({
            limit: limit.toString(),
            offset: offset.toString()
        });
        
        return this.request(`/api/chat/${chatId}/messages?${params.toString()}`, { method: 'GET' });
    },
    
    // Отправка сообщения
    async sendMessage(chatId, message) {
        return this.request(`/api/chat/${chatId}/send`, { 
            method: 'POST', 
            body: JSON.stringify({ message }) 
        });
    },
    
    // Получение списка чатов
    async getMyChats(limit = 50, offset = 0) {
        const params = new URLSearchParams({
            limit: limit.toString(),
            offset: offset.toString()
        });
        
        return this.request(`/api/chat?${params.toString()}`, { method: 'GET' });
    },
    
    // Создание чата для поездки
    async createChatForRide(rideId) {
        return this.request(`/api/chat/ride/${rideId}/start`, { method: 'POST' });
    },
    
    // Загрузка аватара пользователя (ИСПРАВЛЕНО)
    async uploadUserAvatar(imageData) {
        const formData = new FormData();
        formData.append('file', imageData);
        formData.append('file_type', 'avatar');
        
        const data = await this.request('/api/upload/', { 
            method: 'POST', 
            body: formData
            // Не устанавливаем headers для FormData - браузер установит Content-Type автоматически
        });
        
        // Синхронизируем кэш при загрузке файла
        await cacheManager.syncOnDataChange('CREATE', '/api/upload/');
        return data;
    },
    
    // Загрузка фото автомобиля (ИСПРАВЛЕНО)
    async uploadCarPhoto(imageData) {
        const formData = new FormData();
        formData.append('file', imageData);
        formData.append('file_type', 'car');
        
        const data = await this.request('/api/upload/', { 
            method: 'POST', 
            body: formData
            // Не устанавливаем headers для FormData - браузер установит Content-Type автоматически
        });
        
        // Синхронизируем кэш при загрузке файла
        await cacheManager.syncOnDataChange('CREATE', '/api/upload/');
        return data;
    },
    
    // Загрузка фото водительских прав (ИСПРАВЛЕНО)
    async uploadDriverLicense(imageData) {
        const formData = new FormData();
        formData.append('file', imageData);
        formData.append('file_type', 'license');
        
        const data = await this.request('/api/upload/', { 
            method: 'POST', 
            body: formData
            // Не устанавливаем headers для FormData - браузер установит Content-Type автоматически
        });
        
        // Синхронизируем кэш при загрузке файла
        await cacheManager.syncOnDataChange('CREATE', '/api/upload/');
        return data;
    },
    
    // Универсальная загрузка файлов
    async uploadFile(file, fileType) {
        try {
            // Валидация файла
            const maxSize = 5 * 1024 * 1024; // 5MB
            const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
            
            if (file.size > maxSize) {
                throw new Error('Размер файла превышает 5MB');
            }
            
            if (!allowedTypes.includes(file.type)) {
                throw new Error('Неподдерживаемый тип файла. Разрешены: JPEG, PNG, WebP');
            }
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('file_type', fileType);
            
            const result = await this.request('/api/upload/', {
                method: 'POST',
                body: formData
                // Не устанавливаем headers для FormData - браузер установит Content-Type автоматически
            });
            
            // Синхронизируем кэш при загрузке файла
            await cacheManager.syncOnDataChange('CREATE', '/api/upload/');
            return result;
        } catch (error) {
            this.logError(error, 'uploadFile');
            throw error;
        }
    },
    
    // Подписка на уведомления
    async subscribeToNotifications() {
        return this.request('/api/notifications/subscribe', { method: 'POST' });
    },
    
    // Получение настроек уведомлений
    async getNotificationSettings(userId) {
        try {
            const response = await this.request(`/api/notifications/settings/${userId}`, { 
                method: 'GET' 
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения настроек уведомлений:', error);
            throw error;
        }
    },
    
    // Обновление настроек уведомлений
    async updateNotificationSettings(userId, settings) {
        try {
            // Унифицированная структура данных для бэкенда
            const requestData = {
                user_id: userId,
                ride_notifications: settings.ride_notifications,
                system_notifications: settings.system_notifications,
                reminder_notifications: settings.reminder_notifications,
                marketing_notifications: settings.marketing_notifications,
                quiet_hours_start: settings.quiet_hours_start,
                quiet_hours_end: settings.quiet_hours_end,
                email_notifications: settings.email_notifications,
                push_notifications: settings.push_notifications
            };

            const response = await this.request(`/api/notifications/settings/${userId}`, { 
                method: 'PUT', 
                body: JSON.stringify(requestData) 
            });
            return response;
        } catch (error) {
            console.error('Ошибка обновления настроек уведомлений:', error);
            throw error;
        }
    },
    
    // Улучшенная система уведомлений
    async sendNotification(title, message, type = 'info', options = {}) {
        try {
            // Отправляем уведомление на сервер для логирования
            const notificationData = {
                title,
                message,
                type,
                user_id: this.getCurrentUserId(),
                timestamp: new Date().toISOString(),
                ...options
            };
            
            // Асинхронно отправляем на сервер (не блокируем UI)
            this.request('/api/notifications/log', {
                method: 'POST',
                body: JSON.stringify(notificationData)
            }).catch(error => {
                console.warn('Ошибка логирования уведомления:', error);
            });
            
            // Показываем уведомление пользователю
            Utils.showNotification(title, message, type);
            
            // Отправляем в Telegram если настроено
            if (options.send_to_telegram && this.getCurrentUserId()) {
                this.sendTelegramNotification(notificationData).catch(error => {
                    console.warn('Ошибка отправки в Telegram:', error);
                });
            }
            
            return { success: true };
        } catch (error) {
            console.error('Ошибка отправки уведомления:', error);
            // Fallback к локальному уведомлению
            Utils.showNotification(title, message, type);
            return { success: true };
        }
    },
    
    async sendTelegramNotification(notificationData) {
        try {
            const response = await this.request('/api/notifications/telegram', {
                method: 'POST',
                body: JSON.stringify(notificationData)
            });
            return response;
        } catch (error) {
            console.warn('Ошибка отправки в Telegram:', error);
            throw error;
        }
    },
    
    getCurrentUserId() {
        try {
            const currentUser = localStorage.getItem('currentUser');
            if (currentUser) {
                const user = JSON.parse(currentUser);
                return user.id || user.telegram_id;
            }
            return null;
        } catch (error) {
            console.warn('Ошибка получения user_id:', error);
            return null;
        }
    },
    
    // Обновление профиля пользователя
    async updateUserProfile(profileData) {
        const data = await this.request('/api/profile', { 
            method: 'PUT', 
            body: JSON.stringify(profileData) 
        });
        
        // Инвалидируем кэш пользователя
        cacheManager.invalidate('user_data');
        return data;
    },
    
    // Отмена поездки
    async cancelRide(rideId, reason, comment) {
        const params = new URLSearchParams({
            is_driver: 'false'
        });
        
        const data = await this.request(`/api/rides/${rideId}/cancel?${params.toString()}`, { 
            method: 'PUT', 
            body: JSON.stringify({ reason, comment }) 
        });
        
        // Инвалидируем кэш поездок
        cacheManager.invalidate('rides');
        cacheManager.invalidate('my_rides');
        return data;
    },
    
    // Завершение поездки
    async completeRide(rideId) {
        const data = await this.request(`/api/rides/${rideId}/complete`, { method: 'PUT' });
        
        // Инвалидируем кэш поездок
        cacheManager.invalidate('rides');
        cacheManager.invalidate('my_rides');
        return data;
    },
    
    // JWT авторизация
    async login(telegramData) {
        try {
            // Унифицированная структура данных для бэкенда
            const authRequest = {
                user: {
                    id: telegramData.id,
                    first_name: telegramData.first_name,
                    last_name: telegramData.last_name,
                    username: telegramData.username,
                    photo_url: telegramData.photo_url,
                    auth_date: telegramData.auth_date || Math.floor(Date.now() / 1000),
                    hash: telegramData.hash || 'test_hash'
                },
                auth_date: telegramData.auth_date || Math.floor(Date.now() / 1000),
                hash: telegramData.hash || 'test_hash',
                initData: telegramData.initData || '',
                query_id: telegramData.query_id || '',
                start_param: telegramData.start_param || ''
            };

            const response = await this.request('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify(authRequest)
            });

            if (response.tokens) {
                setAuthTokens(response.tokens);
            }

            return response;
        } catch (error) {
            this.logError(error, 'login');
            throw error;
        }
    },
    
    async logout() {
        try {
            await this.request('/api/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            clearAuthTokens();
            cacheManager.clear();
        }
    },
    
    async getCurrentUser() {
        try {
            const response = await this.request('/api/auth/me', { method: 'GET' });
            if (response.success) {
                currentUser = response.user;
                localStorage.setItem('currentUser', JSON.stringify(response.user));
            }
            return response;
        } catch (error) {
            console.error('Get current user error:', error);
            throw error;
        }
    },
    
    // Методы для регистрации и аутентификации
    async verifyTelegramUser(telegramData) {
        try {
            console.log('Sending Telegram verification request:', telegramData);
            
            // Проверяем обязательные поля
            if (!telegramData.user || !telegramData.user.id) {
                throw new Error('Отсутствуют обязательные данные пользователя');
            }
            
            // Унифицированная структура данных для бэкенда
            const requestData = {
                user: {
                    id: telegramData.user.id,
                    first_name: telegramData.user.first_name,
                    last_name: telegramData.user.last_name,
                    username: telegramData.user.username,
                    photo_url: telegramData.user.photo_url,
                    auth_date: telegramData.auth_date || Math.floor(Date.now() / 1000),
                    hash: telegramData.user.hash || telegramData.hash || 'test_hash'
                },
                auth_date: telegramData.auth_date || Math.floor(Date.now() / 1000),
                hash: telegramData.hash || 'test_hash',
                initData: telegramData.initData || '',
                query_id: telegramData.query_id || '',
                start_param: telegramData.start_param || ''
            };
            
            console.log('Prepared request data:', requestData);
            
            const response = await this.request('/api/auth/telegram/verify', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });
            
            console.log('Telegram verification response:', response);
            return response;
        } catch (error) {
            console.error('Ошибка верификации Telegram:', error);
            
            // Возвращаем fallback для нового пользователя
            if (error.response && error.response.status === 500) {
                console.log('Server error, treating as new user');
                return {
                    exists: false,
                    telegram_data: telegramData.user
                };
            }
            
            throw error;
        }
    },

    async registerUser(userData) {
        try {
            const response = await this.request('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка регистрации:', error);
            throw error;
        }
    },

    async updateUserProfileAuth(userId, userData) {
        try {
            const response = await this.request(`/api/auth/profile/${userId}`, {
                method: 'PUT',
                body: JSON.stringify(userData)
            });
            
            // Инвалидируем кэш пользователя
            cacheManager.invalidate('user_data');
            return response;
        } catch (error) {
            console.error('Ошибка обновления профиля:', error);
            throw error;
        }
    },

    async acceptPrivacyPolicy(userId, privacyData) {
        try {
            const response = await this.request(`/api/auth/privacy-policy/accept/${userId}`, {
                method: 'POST',
                body: JSON.stringify(privacyData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка принятия соглашения:', error);
            throw error;
        }
    },

    async getPrivacyPolicy() {
        try {
            const response = await this.request('/api/auth/privacy-policy', {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения соглашения:', error);
            throw error;
        }
    },

    async getUserProfile(userId) {
        const cacheKey = `user_profile_${userId}`;
        const cached = cacheManager.get(cacheKey);
        if (cached) return cached;
        
        try {
            const response = await this.request(`/api/auth/profile/${userId}`, {
                method: 'GET'
            });
            cacheManager.set(cacheKey, response);
            return response;
        } catch (error) {
            console.error('Ошибка получения профиля:', error);
            throw error;
        }
    },

    async getProfileHistory(userId) {
        try {
            const response = await this.request(`/api/auth/profile/${userId}/history`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения истории профиля:', error);
            throw error;
        }
    },

    // Методы для работы с рейтингами и отзывами
    async createRating(ratingData) {
        try {
            // Унифицированная структура данных для бэкенда
            const requestData = {
                target_user_id: ratingData.target_user_id,
                ride_id: ratingData.ride_id,
                rating: ratingData.rating,
                comment: ratingData.comment || null
            };

            const response = await this.request('/api/rating/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            // Синхронизируем кэш при создании рейтинга
            await cacheManager.syncOnDataChange('CREATE', '/api/rating/');
            return response;
        } catch (error) {
            console.error('Ошибка создания рейтинга:', error);
            throw error;
        }
    },

    async createReview(reviewData) {
        try {
            // Унифицированная структура данных для бэкенда
            const requestData = {
                target_user_id: reviewData.target_user_id,
                ride_id: reviewData.ride_id,
                text: reviewData.text,
                is_positive: reviewData.is_positive
            };

            const response = await this.request('/api/rating/review/', {
                method: 'POST',
                body: JSON.stringify(requestData)
            });

            // Синхронизируем кэш при создании отзыва
            await cacheManager.syncOnDataChange('CREATE', '/api/rating/review/');
            return response;
        } catch (error) {
            console.error('Ошибка создания отзыва:', error);
            throw error;
        }
    },

    async getUserRatings(userId, page = 1, limit = 10) {
        const params = new URLSearchParams({
            page: page.toString(),
            limit: limit.toString()
        });
        
        try {
            const response = await this.request(`/api/rating/user/${userId}/?${params.toString()}`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения рейтингов:', error);
            throw error;
        }
    },

    async getUserReviews(userId, page = 1, limit = 10) {
        const params = new URLSearchParams({
            page: page.toString(),
            limit: limit.toString()
        });
        
        try {
            const response = await this.request(`/api/rating/user/${userId}/reviews/?${params.toString()}`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения отзывов:', error);
            throw error;
        }
    },

    async getUserRatingSummary(userId) {
        const cacheKey = `rating_summary_${userId}`;
        const cached = this.cacheManager.get(cacheKey);
        if (cached) return cached;
        
        try {
            const response = await this.request(`/api/rating/user/${userId}/summary/`, {
                method: 'GET'
            });
            this.cacheManager.set(cacheKey, response);
            return response;
        } catch (error) {
            console.error('Ошибка получения сводки рейтингов:', error);
            throw error;
        }
    },

    async getRideRatings(rideId) {
        try {
            const response = await this.request(`/api/rating/ride/${rideId}/`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения рейтингов поездки:', error);
            throw error;
        }
    },

    async getTopUsers(limit = 10) {
        const params = new URLSearchParams({
            limit: limit.toString()
        });
        
        try {
            const response = await this.request(`/api/rating/top/?${params.toString()}`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения топ пользователей:', error);
            throw error;
        }
    },

    async getRatingStatistics() {
        try {
            const response = await this.request('/api/rating/statistics/', {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения статистики рейтингов:', error);
            throw error;
        }
    },

    async updateRating(ratingId, ratingData) {
        try {
            const response = await this.request(`/api/rating/${ratingId}/`, {
                method: 'PUT',
                body: JSON.stringify(ratingData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка обновления рейтинга:', error);
            throw error;
        }
    },

    async deleteRating(ratingId) {
        try {
            const response = await this.request(`/api/rating/${ratingId}/`, {
                method: 'DELETE'
            });
            return response;
        } catch (error) {
            console.error('Ошибка удаления рейтинга:', error);
            throw error;
        }
    },

    async verifyTelegram(telegramData) {
        return this.verifyTelegramUser(telegramData);
    },

    // Методы для модерации
    async createReport(reportData) {
        try {
            const response = await this.request('/api/moderation/report', {
                method: 'POST',
                body: JSON.stringify(reportData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка создания жалобы:', error);
            throw error;
        }
    },

    async checkContent(content) {
        try {
            const response = await this.request('/api/moderation/content/check', {
                method: 'POST',
                body: JSON.stringify({ content })
            });
            return response;
        } catch (error) {
            console.error('Ошибка проверки контента:', error);
            throw error;
        }
    },

    // Методы для работы с уведомлениями
    async sendRideNotification(notificationData) {
        try {
            const response = await this.request('/api/notifications/send/ride', {
                method: 'POST',
                body: JSON.stringify(notificationData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка отправки уведомления о поездке:', error);
            throw error;
        }
    },

    async sendSystemNotification(notificationData) {
        try {
            const response = await this.request('/api/notifications/send/system', {
                method: 'POST',
                body: JSON.stringify(notificationData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка отправки системного уведомления:', error);
            throw error;
        }
    },

    // Утилиты
    clearCache() {
        cacheManager.clear();
    },

    getCacheStats() {
        return {
            size: cacheManager.cache.size,
            keys: Array.from(cacheManager.cache.keys())
        };
    },

    // Новые методы для работы с кэшем
    async syncCache() {
        return await cacheManager.syncWithBackend();
    },

    async invalidateCache(pattern = null) {
        return await cacheManager.invalidateBackend(pattern);
    },

    async clearAllCache() {
        return await cacheManager.clearBackend();
    }
}; 