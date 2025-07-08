import { ERROR_MESSAGES, APP_CONFIG } from '../../config/constants.js';

// Функция для безопасного экранирования HTML
const escapeHtml = (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// Утилиты для валидации и обработки ошибок
export const Utils = {
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
    
    // Обработка ошибок API
    handleApiError: (error, context = 'API') => {
        // Убираем console.error для продакшена, оставляем только логирование в dev режиме
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.error(`API Error in ${context}:`, error);
        }
        
        let message = 'Произошла ошибка при выполнении запроса';
        
        if (error.response) {
            const status = error.response.status;
            const data = error.response.data;
            
            if (status === 401) {
                message = 'Необходима авторизация';
                // Перенаправляем на страницу ограничения
                setTimeout(() => {
                    if (window.router) {
                        window.router.navigate('restricted');
                    }
                }, 2000);
            } else if (status === 403) {
                message = 'Доступ запрещен';
            } else if (status === 404) {
                message = 'Запрашиваемый ресурс не найден';
            } else if (status === 422) {
                message = data?.detail || 'Неверные данные';
            } else if (status >= 500) {
                message = 'Ошибка сервера. Попробуйте позже';
            } else if (data?.detail) {
                message = data.detail;
            }
        } else if (error.request) {
            message = 'Нет соединения с сервером';
        } else if (error.message) {
            message = error.message;
        }
        
        Utils.showNotification('Ошибка', message, 'error');
    },
    
    // Загрузка изображений
    uploadImage: (file, onProgress, onSuccess, onError) => {
        // Имитация загрузки изображения
        const reader = new FileReader();
        
        if (file.size > APP_CONFIG.MAX_FILE_SIZE) {
            onError(ERROR_MESSAGES.FILE_TOO_LARGE);
            return;
        }
        
        if (!file.type.startsWith('image/')) {
            onError(ERROR_MESSAGES.INVALID_FILE_TYPE);
            return;
        }
        
        reader.onload = (e) => {
            // Имитация прогресса загрузки
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress >= 100) {
                    progress = 100;
                    clearInterval(interval);
                    
                    // Имитация успешной загрузки
                    setTimeout(() => {
                        onSuccess(e.target.result);
                    }, 500);
                }
                onProgress(progress);
            }, 200);
        };
        
        reader.onerror = () => {
            onError('Ошибка чтения файла.');
        };
        
        reader.readAsDataURL(file);
    },
    
    // Форматирование времени
    formatTime: (date) => {
        return new Intl.DateTimeFormat('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    },
    
    // Форматирование даты
    formatDate: (date) => {
        return new Intl.DateTimeFormat('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        }).format(date);
    },
    
    // Форматирование даты для отображения
    formatDisplayDate: (dateString) => {
        const date = new Date(dateString);
        const today = new Date();
        const tomorrow = new Date();
        tomorrow.setDate(today.getDate() + 1);
        
        const dayNames = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
        const monthNames = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];
        
        if (date.toDateString() === today.toDateString()) return 'Сегодня';
        if (date.toDateString() === tomorrow.toDateString()) return 'Завтра';
        
        return `${dayNames[date.getDay()]}, ${date.getDate()} ${monthNames[date.getMonth()]}`;
    },
    
    // Показ toast уведомлений
    showToast: (message, type = 'info', duration = 3000) => {
        const toast = document.createElement('div');
        toast.className = `notification alert-${type}`;
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.left = '50%';
        toast.style.transform = 'translateX(-50%)';
        toast.style.zIndex = '10000';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '8px';
        toast.style.color = 'white';
        toast.style.fontWeight = '500';
        toast.style.fontSize = '14px';
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s, transform 0.3s';
        
        if (type === 'success') {
            toast.style.backgroundColor = '#4CAF50';
        } else if (type === 'error') {
            toast.style.backgroundColor = '#f44336';
        } else {
            toast.style.backgroundColor = '#2196F3';
        }
        
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // Анимация появления
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(-50%) translateY(0)';
        }, 100);
        
        // Автоматическое скрытие
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(-50%) translateY(20px)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    },
    
    // Очистка ошибок формы
    clearFormErrors: () => {
        document.querySelectorAll('.form-control.error').forEach(field => {
            Utils.hideFieldError(field);
        });
    },
    
    // Валидация формы
    validateForm: (formData, rules) => {
        const errors = {};
        let isValid = true;
        
        Object.keys(rules).forEach(fieldName => {
            const value = formData[fieldName];
            const fieldRules = rules[fieldName];
            const fieldErrors = Utils.validateField(value, fieldRules);
            
            if (fieldErrors.length > 0) {
                errors[fieldName] = fieldErrors[0];
                isValid = false;
            }
        });
        
        return { isValid, errors };
    },
    
    // Показ ошибок формы
    showFormErrors: (errors) => {
        Object.keys(errors).forEach(fieldName => {
            const field = document.getElementById(fieldName);
            if (field) {
                Utils.showFieldError(field, errors[fieldName]);
            }
        });
    }
};

/**
 * Показывает уведомление в приложении
 * @param {string} message - Текст уведомления
 * @param {string} type - Тип уведомления (success, error, warning, info)
 * @param {number} duration - Длительность показа в миллисекундах
 */
export function showNotification(message, type = 'info', duration = 5000) {
    // Удаляем существующие уведомления
    const existingNotifications = document.querySelectorAll('.app-notification');
    existingNotifications.forEach(notification => {
        notification.remove();
    });

    // Создаем новое уведомление безопасно
    const notification = document.createElement('div');
    notification.className = `app-notification ${type}`;
    
    const content = document.createElement('div');
    content.className = 'notification-content';
    
    const messageElement = document.createElement('div');
    messageElement.className = 'notification-message';
    messageElement.textContent = message;
    
    const closeButton = document.createElement('button');
    closeButton.className = 'notification-close';
    closeButton.innerHTML = '<i class="fas fa-times"></i>';
    closeButton.addEventListener('click', () => {
        notification.remove();
    });
    
    content.appendChild(messageElement);
    content.appendChild(closeButton);
    notification.appendChild(content);

    // Добавляем в DOM
    document.body.appendChild(notification);

    // Автоматически скрываем через указанное время
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.classList.add('hide');
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }
        }, duration);
    }

    return notification;
}

/**
 * Показывает модальное окно подтверждения
 * @param {string} title - Заголовок
 * @param {string} message - Сообщение
 * @param {string} confirmText - Текст кнопки подтверждения
 * @param {string} cancelText - Текст кнопки отмены
 * @returns {Promise<boolean>} - Результат выбора пользователя
 */
export function showConfirmDialog(title, message, confirmText = 'Подтвердить', cancelText = 'Отмена') {
    return new Promise((resolve) => {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        
        const content = document.createElement('div');
        content.className = 'modal-content';
        
        const header = document.createElement('div');
        header.className = 'modal-header';
        const titleElement = document.createElement('h3');
        titleElement.textContent = title;
        header.appendChild(titleElement);
        
        const body = document.createElement('div');
        body.className = 'modal-body';
        const messageElement = document.createElement('p');
        messageElement.textContent = message;
        body.appendChild(messageElement);
        
        const footer = document.createElement('div');
        footer.className = 'modal-footer';
        
        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'btn btn-secondary cancel-btn';
        cancelBtn.textContent = cancelText;
        
        const confirmBtn = document.createElement('button');
        confirmBtn.className = 'btn btn-primary confirm-btn';
        confirmBtn.textContent = confirmText;
        
        footer.appendChild(cancelBtn);
        footer.appendChild(confirmBtn);
        
        content.appendChild(header);
        content.appendChild(body);
        content.appendChild(footer);
        modal.appendChild(content);

        document.body.appendChild(modal);

        const cleanup = () => {
            modal.remove();
        };

        confirmBtn.addEventListener('click', () => {
            cleanup();
            resolve(true);
        });

        cancelBtn.addEventListener('click', () => {
            cleanup();
            resolve(false);
        });

        // Закрытие по клику вне модального окна
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                cleanup();
                resolve(false);
            }
        });
    });
}

/**
 * Показывает модальное окно с загрузкой
 * @param {string} message - Сообщение загрузки
 * @returns {Function} - Функция для скрытия загрузки
 */
export function showLoadingModal(message = 'Загрузка...') {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    const content = document.createElement('div');
    content.className = 'modal-content loading-modal';
    
    const loader = document.createElement('div');
    loader.className = 'loader';
    
    const messageElement = document.createElement('p');
    messageElement.textContent = message;
    
    content.appendChild(loader);
    content.appendChild(messageElement);
    modal.appendChild(content);

    document.body.appendChild(modal);

    return () => {
        modal.remove();
    };
}

/**
 * Форматирует дату в удобочитаемый вид
 * @param {string|Date} date - Дата для форматирования
 * @returns {string} - Отформатированная дата
 */
export function formatDate(date) {
    if (!date) return '';
    
    const d = new Date(date);
    const now = new Date();
    const diffTime = Math.abs(now - d);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
        return 'Сегодня';
    } else if (diffDays === 2) {
        return 'Вчера';
    } else if (diffDays <= 7) {
        return `${diffDays - 1} дней назад`;
    } else {
        return d.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }
}

/**
 * Форматирует время
 * @param {string} time - Время в формате HH:MM
 * @returns {string} - Отформатированное время
 */
export function formatTime(time) {
    if (!time) return '';
    
    const [hours, minutes] = time.split(':');
    return `${hours}:${minutes}`;
}

/**
 * Валидирует номер телефона
 * @param {string} phone - Номер телефона
 * @returns {boolean} - Результат валидации
 */
export function validatePhone(phone) {
    const phoneRegex = /^\+7\s?\(?[0-9]{3}\)?\s?[0-9]{3}-?[0-9]{2}-?[0-9]{2}$/;
    return phoneRegex.test(phone);
}

/**
 * Форматирует номер телефона
 * @param {string} phone - Номер телефона
 * @returns {string} - Отформатированный номер
 */
export function formatPhone(phone) {
    if (!phone) return '';
    
    // Убираем все нецифровые символы
    const digits = phone.replace(/\D/g, '');
    
    if (digits.length === 11 && digits.startsWith('7')) {
        return `+7 (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7, 9)}-${digits.slice(9)}`;
    }
    
    return phone;
}

/**
 * Дебаунс функция
 * @param {Function} func - Функция для выполнения
 * @param {number} wait - Время ожидания в миллисекундах
 * @returns {Function} - Дебаунсированная функция
 */
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Троттлинг функция
 * @param {Function} func - Функция для выполнения
 * @param {number} limit - Лимит времени в миллисекундах
 * @returns {Function} - Троттлированная функция
 */
export function throttle(func, limit) {
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
} 