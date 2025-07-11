import { ERROR_MESSAGES, APP_CONFIG } from '../../config/constants.js';

// Функция для безопасного экранирования HTML
const escapeHtml = (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// Класс для обработки ошибок
class ErrorHandler {
    constructor() {
        this.errorCount = 0;
        this.lastErrorTime = 0;
        this.maxErrorsPerMinute = 10;
    }

    handleError(error, context = 'unknown') {
        const now = Date.now();
        
        // Сброс счетчика ошибок каждую минуту
        if (now - this.lastErrorTime > 60000) {
            this.errorCount = 0;
        }
        
        this.errorCount++;
        this.lastErrorTime = now;
        
        // Логируем ошибку для мониторинга
        this.logError(error, context);
        
        // Показываем пользователю только если не превышен лимит
        if (this.errorCount <= this.maxErrorsPerMinute) {
            this.showUserFriendlyError(error);
        }
    }

    logError(error, context) {
        const errorLog = {
            timestamp: new Date().toISOString(),
            context,
            message: error.message,
            stack: error.stack,
            url: window.location.href,
            userAgent: navigator.userAgent,
            errorType: error.constructor.name
        };

        // В продакшене отправляем в систему мониторинга
        if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            // Здесь можно добавить отправку в Sentry или другую систему
            console.error('Production error:', errorLog);
        } else {
            console.error('Development error:', errorLog);
        }
    }

    showUserFriendlyError(error) {
        let message = 'Произошла ошибка при выполнении запроса';
        
        if (error.status) {
            switch (error.status) {
                case 401:
                    message = 'Необходима авторизация';
                    setTimeout(() => {
                        if (window.router) {
                            window.router.navigate('restricted');
                        }
                    }, 2000);
                    break;
                case 403:
                    message = 'Доступ запрещен';
                    break;
                case 404:
                    message = 'Запрашиваемый ресурс не найден';
                    break;
                case 422:
                    message = error.data?.detail || 'Неверные данные';
                    break;
                case 429:
                    message = 'Слишком много запросов. Попробуйте позже';
                    break;
                case 500:
                    message = 'Ошибка сервера. Попробуйте позже';
                    break;
                default:
                    message = error.data?.detail || message;
            }
        } else if (error.message) {
            message = error.message;
        }

        Utils.showNotification('Ошибка', message, 'error');
    }
}

// Глобальный обработчик ошибок
const errorHandler = new ErrorHandler();

// Утилиты для валидации и обработки ошибок
const Utils = {
    // Валидация полей
    validateField: (value, rules) => {
        const errors = [];
        
        if (rules.required && !value.trim()) {
            errors.push(ERROR_MESSAGES.REQUIRED_FIELD);
        }
        
        if (rules.minLength && value.length < rules.minLength) {
            errors.push(ERROR_MESSAGES.MIN_LENGTH(rules.minLength));
        }
        
        if (rules.maxLength && value.length > rules.maxLength) {
            errors.push(ERROR_MESSAGES.MAX_LENGTH(rules.maxLength));
        }
        
        if (rules.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            errors.push(ERROR_MESSAGES.INVALID_EMAIL);
        }
        
        if (rules.phone && !/^\+?[0-9\s\-\(\)]{10,}$/.test(value)) {
            errors.push(ERROR_MESSAGES.INVALID_PHONE);
        }
        
        if (rules.price && (isNaN(value) || value < 100)) {
            errors.push(ERROR_MESSAGES.MIN_PRICE);
        }
        
        if (rules.date && new Date(value) < new Date()) {
            errors.push(ERROR_MESSAGES.INVALID_DATE);
        }
        
        // Дополнительные правила валидации
        if (rules.telegramId && !/^\d+$/.test(value)) {
            errors.push('ID Telegram должен содержать только цифры');
        }
        
        if (rules.fileSize && value.size > rules.fileSize) {
            errors.push(`Размер файла не должен превышать ${rules.fileSize / (1024 * 1024)}MB`);
        }
        
        if (rules.fileType && !rules.fileType.includes(value.type)) {
            errors.push('Неподдерживаемый тип файла');
        }
        
        return errors;
    },
    
    // Показ ошибок валидации
    showFieldError: (field, message) => {
        field.classList.add('error');
        field.classList.remove('success');
        
        let errorElement = field.parentNode.querySelector('.error-message');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            field.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    },
    
    // Скрытие ошибок валидации
    hideFieldError: (field) => {
        field.classList.remove('error');
        field.classList.add('success');
        
        const errorElement = field.parentNode.querySelector('.error-message');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    },
    
    // Показ уведомлений (исправлено для безопасности)
    showNotification: (title, message, type = 'info', duration = APP_CONFIG.NOTIFICATION_DURATION) => {
        const notification = document.createElement('div');
        notification.className = `notification alert-${type}`;
        
        // Безопасное создание HTML с экранированием
        const titleElement = document.createElement('div');
        titleElement.className = 'notification-title';
        titleElement.textContent = title;
        
        const closeButton = document.createElement('button');
        closeButton.className = 'notification-close';
        closeButton.textContent = '×';
        
        const messageElement = document.createElement('div');
        messageElement.className = 'notification-message';
        messageElement.textContent = message;
        
        const headerElement = document.createElement('div');
        headerElement.className = 'notification-header';
        headerElement.appendChild(titleElement);
        headerElement.appendChild(closeButton);
        
        notification.appendChild(headerElement);
        notification.appendChild(messageElement);
        
        const notificationsContainer = document.getElementById('notifications');
        if (notificationsContainer) {
            notificationsContainer.appendChild(notification);
        } else {
            document.body.appendChild(notification);
        }
        
        // Показываем уведомление
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Автоматическое скрытие
        if (duration > 0) {
            setTimeout(() => {
                Utils.hideNotification(notification);
            }, duration);
        }
        
        // Обработчик закрытия
        closeButton.addEventListener('click', () => {
            Utils.hideNotification(notification);
        });
        
        return notification;
    },
    
    // Скрытие уведомления
    hideNotification: (notification) => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    },
    
    // Обработка ошибок API (улучшенная версия)
    handleApiError: (error, context = 'API') => {
        errorHandler.handleError(error, context);
    },
    
    // Загрузка изображений с оптимизацией
    uploadImage: async (file, onProgress, onSuccess, onError) => {
        try {
            // Валидация файла
            if (file.size > APP_CONFIG.MAX_FILE_SIZE) {
                onError(ERROR_MESSAGES.FILE_TOO_LARGE);
                return;
            }
            
            if (!file.type.startsWith('image/')) {
                onError(ERROR_MESSAGES.INVALID_FILE_TYPE);
                return;
            }
            
            // Оптимизация изображения
            const optimizedFile = await Utils.optimizeImage(file);
            
            // Имитация прогресса загрузки
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    onSuccess(URL.createObjectURL(optimizedFile));
                } else {
                    onProgress(progress);
                }
            }, 100);
            
        } catch (error) {
            onError(error.message);
        }
    },
    
    // Оптимизация изображений
    optimizeImage: async (file, maxSize = 1024, quality = 0.8) => {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();
            
            img.onload = () => {
                // Вычисляем новые размеры
                const ratio = Math.min(maxSize / img.width, maxSize / img.height);
                canvas.width = img.width * ratio;
                canvas.height = img.height * ratio;
                
                // Рисуем изображение с новыми размерами
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                
                // Конвертируем в blob
                canvas.toBlob(resolve, 'image/jpeg', quality);
            };
            
            img.src = URL.createObjectURL(file);
        });
    },
    
    // Валидация формы
    validateForm: (formData, rules) => {
        const errors = {};
        let isValid = true;
        
        for (const [fieldName, fieldRules] of Object.entries(rules)) {
            const field = document.getElementById(fieldName);
            if (field) {
                const fieldErrors = Utils.validateField(field.value, fieldRules);
                if (fieldErrors.length > 0) {
                    errors[fieldName] = fieldErrors[0];
                    isValid = false;
                }
            }
        }
        
        return { isValid, errors };
    },
    
    // Показ ошибок формы
    showFormErrors: (errors) => {
        for (const [fieldName, error] of Object.entries(errors)) {
            const field = document.getElementById(fieldName);
            if (field) {
                Utils.showFieldError(field, error);
            }
        }
    },
    
    // Очистка ошибок формы
    clearFormErrors: () => {
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(element => {
            element.style.display = 'none';
        });
        
        const errorFields = document.querySelectorAll('.error');
        errorFields.forEach(field => {
            field.classList.remove('error');
        });
    },
    
    // Форматирование даты
    formatDisplayDate: (date) => {
        if (!date) return '';
        
        const d = new Date(date);
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        
        if (d.toDateString() === today.toDateString()) {
            return 'Сегодня';
        } else if (d.toDateString() === tomorrow.toDateString()) {
            return 'Завтра';
        } else {
            return d.toLocaleDateString('ru-RU', {
                day: 'numeric',
                month: 'long'
            });
        }
    },
    
    // Форматирование времени
    formatTime: (time) => {
        if (!time) return '';
        
        const d = new Date(time);
        return d.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Валидация телефона
    validatePhone: (phone) => {
        const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
        return /^\+?[0-9]{10,}$/.test(cleanPhone);
    },
    
    // Форматирование телефона
    formatPhone: (phone) => {
        const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
        if (cleanPhone.length === 11 && cleanPhone.startsWith('8')) {
            return '+7' + cleanPhone.slice(1);
        }
        return cleanPhone;
    },
    
    // Debounce функция
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle функция
    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Безопасное создание HTML
    createSafeHTML: (template) => {
        const div = document.createElement('div');
        div.innerHTML = template;
        return div.firstElementChild;
    },
    
    // Проверка онлайн статуса
    isOnline: () => {
        return navigator.onLine;
    },
    
    // Обработчик офлайн/онлайн событий
    setupOnlineHandler: () => {
        window.addEventListener('online', () => {
            Utils.showNotification('Соединение восстановлено', 'Интернет-соединение активно', 'success');
        });
        
        window.addEventListener('offline', () => {
            Utils.showNotification('Нет соединения', 'Проверьте интернет-соединение', 'warning');
        });
    },
    
    // Сохранение в localStorage с обработкой ошибок
    saveToStorage: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Ошибка сохранения в localStorage:', error);
            return false;
        }
    },
    
    // Загрузка из localStorage с обработкой ошибок
    loadFromStorage: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Ошибка загрузки из localStorage:', error);
            return defaultValue;
        }
    },
    
    // Очистка localStorage
    clearStorage: () => {
        try {
            localStorage.clear();
            return true;
        } catch (error) {
            console.error('Ошибка очистки localStorage:', error);
            return false;
        }
    },
    
    // Генерация уникального ID
    generateId: () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },
    
    // Копирование в буфер обмена
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            Utils.showNotification('Скопировано', 'Текст скопирован в буфер обмена', 'success');
            return true;
        } catch (error) {
            console.error('Ошибка копирования:', error);
            return false;
        }
    },
    
    // Проверка поддержки функций браузера
    checkBrowserSupport: () => {
        const support = {
            fetch: typeof fetch !== 'undefined',
            localStorage: typeof localStorage !== 'undefined',
            clipboard: navigator.clipboard && navigator.clipboard.writeText,
            webSocket: typeof WebSocket !== 'undefined',
            fileReader: typeof FileReader !== 'undefined'
        };
        
        return support;
    },
    
    // Получение информации о браузере
    getBrowserInfo: () => {
        return {
            userAgent: navigator.userAgent,
            language: navigator.language,
            platform: navigator.platform,
            cookieEnabled: navigator.cookieEnabled,
            onLine: navigator.onLine
        };
    },
    
    // Мониторинг производительности
    measurePerformance: (name, fn) => {
        const start = performance.now();
        const result = fn();
        const end = performance.now();
        
        console.log(`${name} выполнился за ${(end - start).toFixed(2)}ms`);
        return result;
    },
    
    // Асинхронная версия measurePerformance
    measureAsyncPerformance: async (name, fn) => {
        const start = performance.now();
        const result = await fn();
        const end = performance.now();
        
        console.log(`${name} выполнился за ${(end - start).toFixed(2)}ms`);
        return result;
    }
};

// Экспорт для обратной совместимости
export default Utils;
export function showNotification(message, type = 'info', duration = 5000) {
    return Utils.showNotification('Уведомление', message, type, duration);
}

export function showConfirmDialog(title, message, confirmText = 'Подтвердить', cancelText = 'Отмена') {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <h3>${escapeHtml(title)}</h3>
                <p>${escapeHtml(message)}</p>
                <div class="modal-buttons">
                    <button class="btn btn-secondary" id="cancelBtn">${escapeHtml(cancelText)}</button>
                    <button class="btn btn-primary" id="confirmBtn">${escapeHtml(confirmText)}</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const cleanup = () => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        };
        
        modal.querySelector('#confirmBtn').addEventListener('click', () => {
            cleanup();
            resolve(true);
        });
        
        modal.querySelector('#cancelBtn').addEventListener('click', () => {
            cleanup();
            resolve(false);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                cleanup();
                resolve(false);
            }
        });
    });
}

export function showLoadingModal(message = 'Загрузка...') {
    const modal = document.createElement('div');
    modal.className = 'loading-modal';
    modal.innerHTML = `
        <div class="loading-content">
            <div class="loader"></div>
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    return {
        hide: () => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }
    };
}

export function formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleDateString('ru-RU');
}

export function formatTime(time) {
    if (!time) return '';
    const d = new Date(time);
    return d.toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

export function validatePhone(phone) {
    return Utils.validatePhone(phone);
}

export function formatPhone(phone) {
    return Utils.formatPhone(phone);
}

export function debounce(func, wait) {
    return Utils.debounce(func, wait);
}

export function throttle(func, limit) {
    return Utils.throttle(func, limit);
} 