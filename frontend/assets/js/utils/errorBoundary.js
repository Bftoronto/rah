/**
 * Error Boundary для обработки ошибок в приложении
 * Предоставляет централизованную обработку ошибок и восстановление
 */

class ErrorBoundary {
    constructor() {
        this.errors = [];
        this.maxErrors = 10;
        this.errorHandlers = new Map();
        this.recoveryStrategies = new Map();
        this.isEnabled = true;
        
        // Глобальные обработчики ошибок
        this.setupGlobalHandlers();
    }

    /**
     * Настройка глобальных обработчиков ошибок
     */
    setupGlobalHandlers() {
        // Обработчик необработанных ошибок
        window.addEventListener('error', (event) => {
            this.handleError(event.error || new Error(event.message), {
                type: 'unhandled_error',
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno
            });
        });

        // Обработчик необработанных промисов
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, {
                type: 'unhandled_promise_rejection',
                promise: event.promise
            });
        });

        // Обработчик ошибок загрузки ресурсов
        window.addEventListener('error', (event) => {
            if (event.target && event.target.tagName) {
                this.handleError(new Error(`Failed to load ${event.target.tagName}: ${event.target.src || event.target.href}`), {
                    type: 'resource_load_error',
                    element: event.target.tagName,
                    src: event.target.src || event.target.href
                });
            }
        }, true);
    }

    /**
     * Обработка ошибки
     * @param {Error} error - Объект ошибки
     * @param {Object} context - Контекст ошибки
     */
    handleError(error, context = {}) {
        if (!this.isEnabled) return;

        const errorInfo = {
            message: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            ...context
        };

        // Добавляем ошибку в историю
        this.errors.push(errorInfo);
        if (this.errors.length > this.maxErrors) {
            this.errors.shift();
        }

        // Логируем ошибку
        console.error('ErrorBoundary caught error:', errorInfo);

        // Отправляем ошибку на сервер
        this.reportError(errorInfo);

        // Выполняем обработчик ошибки если есть
        const handler = this.errorHandlers.get(context.type || 'default');
        if (handler) {
            try {
                handler(error, context);
            } catch (handlerError) {
                console.error('Error in error handler:', handlerError);
            }
        }

        // Пытаемся восстановиться
        this.attemptRecovery(error, context);
    }

    /**
     * Регистрация обработчика ошибок
     * @param {string} type - Тип ошибки
     * @param {Function} handler - Обработчик
     */
    registerErrorHandler(type, handler) {
        this.errorHandlers.set(type, handler);
    }

    /**
     * Регистрация стратегии восстановления
     * @param {string} type - Тип ошибки
     * @param {Function} strategy - Стратегия восстановления
     */
    registerRecoveryStrategy(type, strategy) {
        this.recoveryStrategies.set(type, strategy);
    }

    /**
     * Попытка восстановления после ошибки
     * @param {Error} error - Объект ошибки
     * @param {Object} context - Контекст ошибки
     */
    attemptRecovery(error, context) {
        const strategy = this.recoveryStrategies.get(context.type || 'default');
        if (strategy) {
            try {
                strategy(error, context);
            } catch (recoveryError) {
                console.error('Error in recovery strategy:', recoveryError);
                this.showFallbackUI();
            }
        } else {
            this.showFallbackUI();
        }
    }

    /**
     * Показ резервного интерфейса
     */
    showFallbackUI() {
        const fallbackHTML = `
            <div id="error-fallback" style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #f8f9fa;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 9999;
                font-family: Arial, sans-serif;
            ">
                <div style="text-align: center; max-width: 500px; padding: 20px;">
                    <h2 style="color: #dc3545; margin-bottom: 20px;">Что-то пошло не так</h2>
                    <p style="color: #6c757d; margin-bottom: 20px;">
                        Произошла ошибка в приложении. Мы уже работаем над её исправлением.
                    </p>
                    <button onclick="location.reload()" style="
                        background: #007bff;
                        color: white;
                        border: none;
                        padding: 10px 20px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                    ">
                        Обновить страницу
                    </button>
                </div>
            </div>
        `;

        // Удаляем существующий fallback если есть
        const existingFallback = document.getElementById('error-fallback');
        if (existingFallback) {
            existingFallback.remove();
        }

        document.body.insertAdjacentHTML('beforeend', fallbackHTML);
    }

    /**
     * Отправка ошибки на сервер
     * @param {Object} errorInfo - Информация об ошибке
     */
    async reportError(errorInfo) {
        try {
            const payload = {
                type: errorInfo.type || 'UnhandledError',
                data: { ...errorInfo }
            };
            await fetch('/api/monitoring/errors', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });
        } catch (reportError) {
            console.error('Failed to report error:', reportError);
        }
    }

    /**
     * Получение статистики ошибок
     * @returns {Object} Статистика ошибок
     */
    getErrorStats() {
        const stats = {
            total: this.errors.length,
            byType: {},
            recent: this.errors.slice(-5)
        };

        this.errors.forEach(error => {
            const type = error.type || 'unknown';
            stats.byType[type] = (stats.byType[type] || 0) + 1;
        });

        return stats;
    }

    /**
     * Очистка истории ошибок
     */
    clearErrors() {
        this.errors = [];
    }

    /**
     * Включение/выключение Error Boundary
     * @param {boolean} enabled - Включить или выключить
     */
    setEnabled(enabled) {
        this.isEnabled = enabled;
    }

    /**
     * Проверка критичности ошибки
     * @param {Error} error - Объект ошибки
     * @returns {boolean} Критична ли ошибка
     */
    isCriticalError(error) {
        const criticalPatterns = [
            /network error/i,
            /authentication failed/i,
            /session expired/i,
            /database connection/i
        ];

        return criticalPatterns.some(pattern => pattern.test(error.message));
    }

    /**
     * Создание пользовательской ошибки
     * @param {string} message - Сообщение ошибки
     * @param {string} type - Тип ошибки
     * @param {Object} context - Дополнительный контекст
     */
    createError(message, type = 'custom', context = {}) {
        const error = new Error(message);
        error.type = type;
        error.context = context;
        this.handleError(error, { type, ...context });
        return error;
    }
}

// Создаем глобальный экземпляр Error Boundary
const errorBoundary = new ErrorBoundary();

// Регистрируем обработчики для различных типов ошибок
errorBoundary.registerErrorHandler('api_error', (error, context) => {
    console.error('API Error:', error);
    // Показываем пользователю уведомление об ошибке API
    if (window.showNotification) {
        window.showNotification('Ошибка соединения с сервером', 'error');
    }
});

errorBoundary.registerErrorHandler('validation_error', (error, context) => {
    console.error('Validation Error:', error);
    // Показываем пользователю ошибку валидации
    if (window.showNotification) {
        window.showNotification('Ошибка в данных формы', 'warning');
    }
});

errorBoundary.registerErrorHandler('auth_error', (error, context) => {
    console.error('Auth Error:', error);
    // Перенаправляем на страницу входа
    if (window.location.pathname !== '/login') {
        window.location.href = '/login';
    }
});

// Регистрируем стратегии восстановления
errorBoundary.registerRecoveryStrategy('api_error', (error, context) => {
    // Пытаемся повторить запрос через некоторое время
    setTimeout(() => {
        if (context.retryCount < 3) {
            context.retryCount = (context.retryCount || 0) + 1;
            // Повторяем оригинальный запрос
            if (context.originalRequest) {
                context.originalRequest();
            }
        }
    }, 1000 * (context.retryCount || 1));
});

errorBoundary.registerRecoveryStrategy('auth_error', (error, context) => {
    // Очищаем локальное хранилище и перенаправляем
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = '/login';
});

// Экспортируем для использования в других модулях
window.errorBoundary = errorBoundary;

// Утилитарные функции для использования в коде
window.handleError = (error, context) => errorBoundary.handleError(error, context);
window.createError = (message, type, context) => errorBoundary.createError(message, type, context);
window.getErrorStats = () => errorBoundary.getErrorStats(); 