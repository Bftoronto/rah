import { Utils } from './utils.js';

// Класс для мониторинга производительности и ошибок
class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoads: 0,
            apiCalls: 0,
            errors: 0,
            slowOperations: 0
        };
        this.startTime = performance.now();
        this.observers = [];
        this.isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
    }

    // Инициализация мониторинга
    init() {
        this.setupPerformanceObserver();
        this.setupErrorObserver();
        this.setupNetworkObserver();
        this.setupUserInteractionObserver();
        
        // Отправляем метрики каждые 30 секунд
        setInterval(() => {
            this.sendMetrics();
        }, 30000);
    }

    // Настройка наблюдения за производительностью
    setupPerformanceObserver() {
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        this.handlePerformanceEntry(entry);
                    }
                });
                
                observer.observe({ entryTypes: ['navigation', 'resource', 'paint'] });
                this.observers.push(observer);
            } catch (error) {
                console.error('Ошибка настройки PerformanceObserver:', error);
            }
        }
    }

    // Настройка наблюдения за ошибками
    setupErrorObserver() {
        window.addEventListener('error', (event) => {
            this.handleError(event.error || event.message, 'javascript');
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason, 'promise');
        });
    }

    // Настройка наблюдения за сетью
    setupNetworkObserver() {
        if ('navigator' in window && 'connection' in navigator) {
            const connection = navigator.connection;
            if (connection) {
                connection.addEventListener('change', () => {
                    this.logNetworkChange(connection);
                });
            }
        }
    }

    // Настройка наблюдения за взаимодействием пользователя
    setupUserInteractionObserver() {
        let lastInteraction = Date.now();
        
        const events = ['click', 'input', 'scroll', 'keydown'];
        events.forEach(eventType => {
            document.addEventListener(eventType, () => {
                lastInteraction = Date.now();
            }, { passive: true });
        });

        // Проверяем активность пользователя каждые 5 минут
        setInterval(() => {
            const timeSinceLastInteraction = Date.now() - lastInteraction;
            if (timeSinceLastInteraction > 300000) { // 5 минут
                this.logUserInactivity(timeSinceLastInteraction);
            }
        }, 300000);
    }

    // Обработка записей производительности
    handlePerformanceEntry(entry) {
        switch (entry.entryType) {
            case 'navigation':
                this.handleNavigationEntry(entry);
                break;
            case 'resource':
                this.handleResourceEntry(entry);
                break;
            case 'paint':
                this.handlePaintEntry(entry);
                break;
        }
    }

    // Обработка навигации
    handleNavigationEntry(entry) {
        const metrics = {
            type: 'navigation',
            url: window.location.href,
            loadTime: entry.loadEventEnd - entry.loadEventStart,
            domContentLoaded: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
            firstPaint: entry.firstPaint,
            firstContentfulPaint: entry.firstContentfulPaint
        };

        this.logMetric('navigation', metrics);
        
        // Предупреждение о медленной загрузке
        if (metrics.loadTime > 3000) {
            this.logSlowOperation('page_load', metrics.loadTime);
        }
    }

    // Обработка ресурсов
    handleResourceEntry(entry) {
        const metrics = {
            type: 'resource',
            name: entry.name,
            duration: entry.duration,
            size: entry.transferSize,
            initiatorType: entry.initiatorType
        };

        this.logMetric('resource', metrics);
        
        // Предупреждение о медленных ресурсах
        if (entry.duration > 1000) {
            this.logSlowOperation('resource_load', entry.duration, entry.name);
        }
    }

    // Обработка отрисовки
    handlePaintEntry(entry) {
        const metrics = {
            type: 'paint',
            name: entry.name,
            startTime: entry.startTime
        };

        this.logMetric('paint', metrics);
    }

    // Обработка ошибок
    handleError(error, type) {
        this.metrics.errors++;
        
        const errorData = {
            type: type,
            message: error.message || error,
            stack: error.stack,
            url: window.location.href,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent
        };

        this.logError(errorData);
    }

    // Логирование метрик
    logMetric(category, data) {
        const metric = {
            category,
            data,
            timestamp: Date.now(),
            sessionId: this.getSessionId()
        };

        if (this.isProduction) {
            // В продакшене отправляем в систему мониторинга
            this.sendToMonitoring(metric);
        } else {
            // В разработке выводим в консоль
            console.log('Metric:', metric);
        }
    }

    // Логирование ошибок
    logError(errorData) {
        if (this.isProduction) {
            // В продакшене отправляем в систему мониторинга
            this.sendToMonitoring({
                type: 'error',
                data: errorData,
                timestamp: Date.now(),
                sessionId: this.getSessionId()
            });
        } else {
            console.error('Error:', errorData);
        }
    }

    // Логирование медленных операций
    logSlowOperation(operation, duration, details = '') {
        this.metrics.slowOperations++;
        
        const slowOpData = {
            operation,
            duration,
            details,
            url: window.location.href,
            timestamp: new Date().toISOString()
        };

        this.logMetric('slow_operation', slowOpData);
    }

    // Логирование изменений сети
    logNetworkChange(connection) {
        const networkData = {
            effectiveType: connection.effectiveType,
            downlink: connection.downlink,
            rtt: connection.rtt,
            saveData: connection.saveData
        };

        this.logMetric('network_change', networkData);
    }

    // Логирование неактивности пользователя
    logUserInactivity(duration) {
        this.logMetric('user_inactivity', {
            duration,
            timestamp: new Date().toISOString()
        });
    }

    // Отправка метрик в систему мониторинга
    sendToMonitoring(data) {
        // Здесь можно добавить отправку в Sentry, DataDog или другую систему
        if (this.isProduction) {
            // Имитация отправки в систему мониторинга
            console.log('Sending to monitoring:', data);
        }
    }

    // Отправка агрегированных метрик
    sendMetrics() {
        const sessionDuration = performance.now() - this.startTime;
        
        const aggregatedMetrics = {
            sessionId: this.getSessionId(),
            timestamp: Date.now(),
            duration: sessionDuration,
            metrics: this.metrics,
            userAgent: navigator.userAgent,
            url: window.location.href,
            memory: this.getMemoryInfo(),
            network: this.getNetworkInfo()
        };

        this.sendToMonitoring({
            type: 'aggregated_metrics',
            data: aggregatedMetrics
        });

        // Сбрасываем счетчики
        this.metrics = {
            pageLoads: 0,
            apiCalls: 0,
            errors: 0,
            slowOperations: 0
        };
    }

    // Получение информации о памяти
    getMemoryInfo() {
        if ('memory' in performance) {
            return {
                usedJSHeapSize: performance.memory.usedJSHeapSize,
                totalJSHeapSize: performance.memory.totalJSHeapSize,
                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
            };
        }
        return null;
    }

    // Получение информации о сети
    getNetworkInfo() {
        if ('connection' in navigator) {
            const connection = navigator.connection;
            return {
                effectiveType: connection.effectiveType,
                downlink: connection.downlink,
                rtt: connection.rtt,
                saveData: connection.saveData
            };
        }
        return null;
    }

    // Получение ID сессии
    getSessionId() {
        let sessionId = sessionStorage.getItem('monitoring_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('monitoring_session_id', sessionId);
        }
        return sessionId;
    }

    // Измерение производительности функции
    measureFunction(name, fn) {
        const start = performance.now();
        const result = fn();
        const duration = performance.now() - start;
        
        this.logMetric('function_performance', {
            name,
            duration,
            timestamp: Date.now()
        });
        
        if (duration > 100) {
            this.logSlowOperation('function_call', duration, name);
        }
        
        return result;
    }

    // Измерение производительности асинхронной функции
    async measureAsyncFunction(name, fn) {
        const start = performance.now();
        const result = await fn();
        const duration = performance.now() - start;
        
        this.logMetric('async_function_performance', {
            name,
            duration,
            timestamp: Date.now()
        });
        
        if (duration > 100) {
            this.logSlowOperation('async_function_call', duration, name);
        }
        
        return result;
    }

    // Очистка ресурсов
    destroy() {
        this.observers.forEach(observer => {
            if (observer.disconnect) {
                observer.disconnect();
            }
        });
        this.observers = [];
    }
}

// Глобальный экземпляр мониторинга
const performanceMonitor = new PerformanceMonitor();

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    performanceMonitor.init();
});

// Экспорт для использования в других модулях
export { PerformanceMonitor, performanceMonitor }; 