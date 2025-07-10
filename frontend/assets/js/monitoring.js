/**
 * Система мониторинга производительности для фронтенда
 */

class PerformanceMonitor {
    constructor() {
        this.metrics = {
            apiCalls: 0,
            errors: 0,
            responseTimes: [],
            cacheHits: 0,
            cacheMisses: 0,
            pageLoads: 0,
            userInteractions: 0
        };
        this.startTime = Date.now();
        this.sessionId = this.generateSessionId();
        this.initializeMonitoring();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    initializeMonitoring() {
        // Мониторинг загрузки страниц
        this.trackPageLoad();
        
        // Мониторинг ошибок
        this.trackErrors();
        
        // Мониторинг производительности
        this.trackPerformance();
        
        // Периодическая отправка метрик
        setInterval(() => {
            this.sendMetrics();
        }, 60000); // Каждую минуту
    }

    trackPageLoad() {
        window.addEventListener('load', () => {
            this.metrics.pageLoads++;
            
            // Измеряем время загрузки страницы
            const loadTime = performance.now();
            this.metrics.responseTimes.push(loadTime);
            
            // Ограничиваем массив последними 100 значениями
            if (this.metrics.responseTimes.length > 100) {
                this.metrics.responseTimes.shift();
            }
        });
    }

    trackErrors() {
        window.addEventListener('error', (event) => {
            this.metrics.errors++;
            this.logError('JavaScript Error', {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error?.stack
            });
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.metrics.errors++;
            this.logError('Unhandled Promise Rejection', {
                reason: event.reason
            });
        });
    }

    trackPerformance() {
        // Мониторинг FPS
        let frameCount = 0;
        let lastTime = performance.now();
        
        const countFrames = () => {
            frameCount++;
            const currentTime = performance.now();
            
            if (currentTime - lastTime >= 1000) {
                const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                this.trackMetric('fps', fps);
                frameCount = 0;
                lastTime = currentTime;
            }
            
            requestAnimationFrame(countFrames);
        };
        
        requestAnimationFrame(countFrames);
    }

    trackApiCall(endpoint, method, startTime) {
        this.metrics.apiCalls++;
        const duration = Date.now() - startTime;
        this.metrics.responseTimes.push(duration);
        
        // Ограничиваем массив последними 100 значениями
        if (this.metrics.responseTimes.length > 100) {
            this.metrics.responseTimes.shift();
        }
        
        this.trackMetric('api_call', {
            endpoint,
            method,
            duration,
            timestamp: Date.now()
        });
    }

    trackError(error, context = '') {
        this.metrics.errors++;
        this.logError('API Error', {
            message: error.message,
            status: error.status,
            context,
            timestamp: Date.now()
        });
    }

    trackCacheHit() {
        this.metrics.cacheHits++;
        this.trackMetric('cache_hit', Date.now());
    }

    trackCacheMiss() {
        this.metrics.cacheMisses++;
        this.trackMetric('cache_miss', Date.now());
    }

    trackUserInteraction(type, data = {}) {
        this.metrics.userInteractions++;
        this.trackMetric('user_interaction', {
            type,
            data,
            timestamp: Date.now()
        });
    }

    trackMetric(name, value) {
        // Сохраняем метрику в localStorage для анализа
        const metrics = JSON.parse(localStorage.getItem('performance_metrics') || '{}');
        if (!metrics[name]) {
            metrics[name] = [];
        }
        metrics[name].push({
            value,
            timestamp: Date.now()
        });
        
        // Ограничиваем количество записей
        if (metrics[name].length > 100) {
            metrics[name] = metrics[name].slice(-100);
        }
        
        localStorage.setItem('performance_metrics', JSON.stringify(metrics));
    }

    getMetrics() {
        const avgResponseTime = this.metrics.responseTimes.length > 0 
            ? this.metrics.responseTimes.reduce((a, b) => a + b, 0) / this.metrics.responseTimes.length 
            : 0;
        
        const cacheHitRate = this.metrics.cacheHits + this.metrics.cacheMisses > 0
            ? (this.metrics.cacheHits / (this.metrics.cacheHits + this.metrics.cacheMisses)) * 100
            : 0;

        const errorRate = this.metrics.apiCalls > 0 
            ? (this.metrics.errors / this.metrics.apiCalls) * 100 
            : 0;

        return {
            sessionId: this.sessionId,
            uptime: Date.now() - this.startTime,
            apiCalls: this.metrics.apiCalls,
            errors: this.metrics.errors,
            avgResponseTime: Math.round(avgResponseTime),
            cacheHitRate: Math.round(cacheHitRate),
            errorRate: Math.round(errorRate),
            pageLoads: this.metrics.pageLoads,
            userInteractions: this.metrics.userInteractions,
            userAgent: navigator.userAgent,
            screenResolution: `${screen.width}x${screen.height}`,
            language: navigator.language,
            timestamp: Date.now()
        };
    }

    logError(type, data) {
        const errorLog = {
            type,
            data,
            sessionId: this.sessionId,
            timestamp: Date.now(),
            url: window.location.href,
            userAgent: navigator.userAgent
        };
        
        console.error('Performance Monitor Error:', errorLog);
        
        // В продакшене отправляем в систему мониторинга
        if (this.isProduction()) {
            this.sendErrorToServer(errorLog);
        }
    }

    sendMetrics() {
        const metrics = this.getMetrics();
        
        // Отправляем метрики на сервер для мониторинга
        fetch('/api/monitoring/metrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(metrics)
        }).catch(error => {
            console.error('Failed to send metrics:', error);
        });
    }

    sendErrorToServer(errorLog) {
        fetch('/api/monitoring/errors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(errorLog)
        }).catch(error => {
            console.error('Failed to send error log:', error);
        });
    }

    isProduction() {
        return window.location.hostname !== 'localhost' && 
               window.location.hostname !== '127.0.0.1';
    }

    // Методы для интеграции с API
    wrapApiCall(apiCall) {
        return async (...args) => {
            const startTime = Date.now();
            try {
                const result = await apiCall(...args);
                this.trackApiCall(args[0] || 'unknown', 'GET', startTime);
                return result;
            } catch (error) {
                this.trackError(error, 'api_call');
                throw error;
            }
        };
    }

    // Методы для интеграции с кэшем
    wrapCacheGet(cacheGet) {
        return (key) => {
            const result = cacheGet(key);
            if (result) {
                this.trackCacheHit();
            } else {
                this.trackCacheMiss();
            }
            return result;
        };
    }

    // Получение статистики производительности
    getPerformanceStats() {
        const metrics = this.getMetrics();
        const cacheStats = window.cacheManager?.getStats() || {};
        
        return {
            ...metrics,
            cache: cacheStats,
            memory: this.getMemoryInfo(),
            network: this.getNetworkInfo()
        };
    }

    getMemoryInfo() {
        if (performance.memory) {
            return {
                usedJSHeapSize: performance.memory.usedJSHeapSize,
                totalJSHeapSize: performance.memory.totalJSHeapSize,
                jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
            };
        }
        return null;
    }

    getNetworkInfo() {
        if ('connection' in navigator) {
            return {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            };
        }
        return null;
    }
}

// Глобальный экземпляр мониторинга
window.performanceMonitor = new PerformanceMonitor();

// Экспорт для использования в других модулях
export { PerformanceMonitor }; 