import { Utils } from './utils.js';

// Конфигурация API
const API_CONFIG = {
    // Локальная разработка
    development: {
        baseURL: 'http://localhost:8000',
        timeout: 10000
    },
    // GitHub Pages (демо)
    production: {
        baseURL: 'https://rah.pages.dev/api',
        timeout: 15000
    },
    // Telegram Mini App
    telegram: {
        baseURL: 'https://your-backend-domain.com/api',
        timeout: 10000
    }
};

// Определение окружения
const getEnvironment = () => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'development';
    } else if (window.location.hostname === 'rah.pages.dev') {
        return 'production';
    } else if (window.Telegram && window.Telegram.WebApp) {
        return 'telegram';
    }
    return 'production';
};

const currentConfig = API_CONFIG[getEnvironment()];

// API клиент для работы с сервером
export const API = {
    // Общий метод для запросов
    async request(endpoint, options = {}) {
        const url = `${currentConfig.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const error = new Error(`HTTP error! status: ${response.status}`);
                error.response = response;
                error.data = errorData;
                throw error;
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    // Получение данных пользователя
    async getUserData() {
        return this.request('/profile', { method: 'GET' });
    },
    
    // Поиск поездок
    async getRides(from, to, date) {
        return this.request(`/rides?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}&date=${encodeURIComponent(date)}`, { method: 'GET' });
    },
    
    // Бронирование поездки
    async bookRide(rideId) {
        return this.request(`/rides/${rideId}/book`, { method: 'POST' });
    },
    
    // Создание поездки
    async createRide(rideData) {
        return this.request('/rides', { method: 'POST', body: JSON.stringify(rideData) });
    },
    
    // Обработка платежа
    async processPayment(amount, method) {
        return this.request('/payment/pay', { method: 'POST', body: JSON.stringify({ amount, method }) });
    },
    
    // Получение моих поездок
    async getMyRides() {
        return this.request('/rides/my', { method: 'GET' });
    },
    
    // Получение сообщений чата
    async getChatMessages(chatId) {
        return this.request(`/chat/${chatId}`, { method: 'GET' });
    },
    
    // Отправка сообщения
    async sendMessage(chatId, message) {
        return this.request(`/chat/${chatId}`, { method: 'POST', body: JSON.stringify({ message }) });
    },
    
    // Загрузка аватара пользователя
    async uploadUserAvatar(imageData) {
        return this.request('/upload', { method: 'POST', body: JSON.stringify({ file: imageData, type: 'avatar' }) });
    },
    
    // Загрузка фото автомобиля
    async uploadCarPhoto(imageData) {
        return this.request('/upload', { method: 'POST', body: JSON.stringify({ file: imageData, type: 'car' }) });
    },
    
    // Загрузка фото паспорта
    async uploadPassportPhoto(imageData) {
        return this.request('/upload', { method: 'POST', body: JSON.stringify({ file: imageData, type: 'passport' }) });
    },
    
    // Подписка на уведомления (заглушка)
    async subscribeToNotifications() {
        return { success: true, subscriptionId: 'sub_' + Date.now() };
    },
    
    // Отправка уведомления (заглушка)
    async sendNotification(title, message, type = 'info') {
        Utils.showNotification(title, message, type);
        return { success: true };
    },
    
    // Обновление профиля пользователя
    async updateUserProfile(profileData) {
        return this.request('/profile', { method: 'PUT', body: JSON.stringify(profileData) });
    },
    
    // Отмена поездки
    async cancelRide(rideId, reason, comment) {
        return this.request(`/rides/${rideId}/cancel`, { method: 'POST', body: JSON.stringify({ reason, comment }) });
    },
    
    // Методы для регистрации и аутентификации
    async verifyTelegramUser(telegramData) {
        try {
            const response = await this.request('/auth/telegram/verify', {
                method: 'POST',
                body: JSON.stringify(telegramData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка верификации Telegram:', error);
            throw error;
        }
    },

    async registerUser(userData) {
        try {
            const response = await this.request('/auth/register', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка регистрации:', error);
            throw error;
        }
    },

    async updateUserProfile(userId, userData) {
        try {
            const response = await this.request(`/auth/profile/${userId}`, {
                method: 'PUT',
                body: JSON.stringify(userData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка обновления профиля:', error);
            throw error;
        }
    },

    async acceptPrivacyPolicy(userId, privacyData) {
        try {
            const response = await this.request(`/auth/privacy-policy/accept/${userId}`, {
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
            const response = await this.request('/auth/privacy-policy', {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения соглашения:', error);
            throw error;
        }
    },

    async getUserProfile(userId) {
        try {
            const response = await this.request(`/auth/profile/${userId}`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения профиля:', error);
            throw error;
        }
    },

    async getProfileHistory(userId) {
        try {
            const response = await this.request(`/auth/profile/${userId}/history`, {
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
            const response = await this.request('/rating', {
                method: 'POST',
                body: JSON.stringify(ratingData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка создания рейтинга:', error);
            throw error;
        }
    },

    async createReview(reviewData) {
        try {
            const response = await this.request('/rating/review', {
                method: 'POST',
                body: JSON.stringify(reviewData)
            });
            return response;
        } catch (error) {
            console.error('Ошибка создания отзыва:', error);
            throw error;
        }
    },

    async getUserRatings(userId, page = 1, limit = 10) {
        try {
            const response = await this.request(`/rating/user/${userId}?page=${page}&limit=${limit}`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения рейтингов:', error);
            throw error;
        }
    },

    async getUserReviews(userId, page = 1, limit = 10) {
        try {
            const response = await this.request(`/rating/user/${userId}/reviews?page=${page}&limit=${limit}`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения отзывов:', error);
            throw error;
        }
    },

    async getUserRatingSummary(userId) {
        try {
            const response = await this.request(`/rating/user/${userId}/summary`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения сводки рейтингов:', error);
            throw error;
        }
    },

    async getRideRatings(rideId) {
        try {
            const response = await this.request(`/rating/ride/${rideId}`, {
                method: 'GET'
            });
            return response;
        } catch (error) {
            console.error('Ошибка получения рейтингов поездки:', error);
            throw error;
        }
    },

    async getTopUsers(limit = 10) {
        try {
            const response = await this.request(`/rating/top?limit=${limit}`, {
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
            const response = await this.request('/rating/statistics', {
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
            const response = await this.request(`/rating/${ratingId}`, {
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
            const response = await this.request(`/rating/${ratingId}`, {
                method: 'DELETE'
            });
            return response;
        } catch (error) {
            console.error('Ошибка удаления рейтинга:', error);
            throw error;
        }
    }
}; 