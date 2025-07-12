// Мониторинг ошибок фронтенда - исправленная версия
class ErrorMonitor {
    constructor() {
        this.errorCount = 0;
        this.lastErrorTime = null;
        this.errorTypes = new Map();
        this.isMonitoring = false;
    }

    start() {
        if (this.isMonitoring) return;
        
        console.log('🚀 Запуск мониторинга ошибок...');
        this.isMonitoring = true;
        
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

        // Обработчик ошибок модулей
        window.addEventListener('error', (event) => {
            if (event.message && event.message.includes('import')) {
                this.handleError(event.error || new Error(event.message), {
                    type: 'module_import_error',
                    filename: event.filename
                });
            }
        });

        console.log('✅ Мониторинг ошибок запущен');
    }

    handleError(error, context = {}) {
        this.errorCount++;
        this.lastErrorTime = new Date();
        
        const errorType = context.type || 'unknown';
        this.errorTypes.set(errorType, (this.errorTypes.get(errorType) || 0) + 1);
        
        const errorInfo = {
            message: error.message,
            stack: error.stack,
            type: errorType,
            context: context,
            timestamp: this.lastErrorTime.toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        console.error('🚨 Ошибка фронтенда:', errorInfo);
        
        // Отправляем ошибку на сервер
        this.sendErrorToServer(errorInfo);
        
        // Показываем уведомление пользователю
        this.showUserNotification(error);
    }

    async sendErrorToServer(errorInfo) {
        try {
            const response = await fetch('/api/monitoring/errors', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(errorInfo)
            });
            
            if (!response.ok) {
                console.error('Ошибка отправки ошибки на сервер:', response.status);
            }
        } catch (error) {
            console.error('Ошибка отправки ошибки на сервер:', error);
        }
    }

    showUserNotification(error) {
        // Создаем уведомление для пользователя
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f44336;
            color: white;
            padding: 15px;
            border-radius: 5px;
            z-index: 10000;
            max-width: 300px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        
        notification.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 5px;">Ошибка приложения</div>
            <div style="font-size: 12px;">${error.message}</div>
            <button onclick="this.parentElement.remove()" style="
                position: absolute;
                top: 5px;
                right: 5px;
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                font-size: 16px;
            ">×</button>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматически удаляем через 10 секунд
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 10000);
    }

    getStats() {
        return {
            totalErrors: this.errorCount,
            lastErrorTime: this.lastErrorTime,
            errorTypes: Object.fromEntries(this.errorTypes),
            isMonitoring: this.isMonitoring
        };
    }

    stop() {
        this.isMonitoring = false;
        console.log('⏹️ Мониторинг ошибок остановлен');
    }
}

// Создаем глобальный экземпляр мониторинга
window.errorMonitor = new ErrorMonitor();

// Автоматически запускаем мониторинг при загрузке
document.addEventListener('DOMContentLoaded', () => {
    window.errorMonitor.start();
});

// Экспорт для использования в других модулях
export { ErrorMonitor }; 