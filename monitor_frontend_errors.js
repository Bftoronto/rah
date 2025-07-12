#!/usr/bin/env node

/**
 * Скрипт мониторинга ошибок фронтенда
 * Отслеживает ошибки в реальном времени и отправляет уведомления
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

class FrontendErrorMonitor {
    constructor() {
        this.errorLog = [];
        this.lastCheck = new Date();
        this.config = {
            backendUrl: 'https://pax-backend-2gng.onrender.com',
            checkInterval: 30000, // 30 секунд
            maxErrors: 10,
            alertThreshold: 3
        };
    }

    /**
     * Проверка состояния фронтенда
     */
    async checkFrontendHealth() {
        try {
            console.log(`🔍 Проверка фронтенда: ${new Date().toISOString()}`);
            
            // Проверяем доступность основных файлов
            const criticalFiles = [
                'frontend/index.html',
                'frontend/assets/js/app.js',
                'frontend/assets/js/state.js',
                'frontend/assets/js/api.js'
            ];
            
            for (const file of criticalFiles) {
                if (!fs.existsSync(file)) {
                    this.logError(`Критический файл не найден: ${file}`);
                }
            }
            
            // Проверяем синтаксис JavaScript файлов
            await this.validateJavaScriptFiles();
            
            // Проверяем API бэкенда
            await this.checkBackendHealth();
            
            // Проверяем ошибки в логах
            await this.checkErrorLogs();
            
        } catch (error) {
            this.logError(`Ошибка проверки фронтенда: ${error.message}`);
        }
    }

    /**
     * Валидация JavaScript файлов
     */
    async validateJavaScriptFiles() {
        const jsFiles = this.findJavaScriptFiles('frontend/assets/js');
        
        for (const file of jsFiles) {
            try {
                const content = fs.readFileSync(file, 'utf8');
                
                // Проверяем на наличие проблемных паттернов
                const issues = this.findJavaScriptIssues(content, file);
                
                if (issues.length > 0) {
                    issues.forEach(issue => this.logError(issue));
                }
                
            } catch (error) {
                this.logError(`Ошибка чтения файла ${file}: ${error.message}`);
            }
        }
    }

    /**
     * Поиск JavaScript файлов
     */
    findJavaScriptFiles(dir) {
        const files = [];
        
        function scanDirectory(currentDir) {
            const items = fs.readdirSync(currentDir);
            
            for (const item of items) {
                const fullPath = path.join(currentDir, item);
                const stat = fs.statSync(fullPath);
                
                if (stat.isDirectory()) {
                    scanDirectory(fullPath);
                } else if (item.endsWith('.js')) {
                    files.push(fullPath);
                }
            }
        }
        
        scanDirectory(dir);
        return files;
    }

    /**
     * Поиск проблем в JavaScript коде
     */
    findJavaScriptIssues(content, filename) {
        const issues = [];
        
        // Проверка на конфликтующие экспорты
        const hasNamedExport = /export\s*\{[^}]*\}/.test(content);
        const hasDefaultExport = /export\s+default/.test(content);
        
        if (hasNamedExport && hasDefaultExport) {
            issues.push(`Конфликтующие экспорты в ${filename}`);
        }
        
        // Проверка на неиспользуемые импорты
        const importMatches = content.match(/import\s+.*?from\s+['"][^'"]+['"]/g);
        if (importMatches) {
            importMatches.forEach(importStmt => {
                const importName = importStmt.match(/import\s+(\{[^}]*\}|\w+)/);
                if (importName && !content.includes(importName[1])) {
                    issues.push(`Возможно неиспользуемый импорт в ${filename}: ${importStmt}`);
                }
            });
        }
        
        // Проверка на синтаксические ошибки
        try {
            // Простая проверка на базовые синтаксические ошибки
            if (content.includes('export * from') && !content.includes('export {')) {
                issues.push(`Потенциальная проблема с re-export в ${filename}`);
            }
        } catch (error) {
            issues.push(`Синтаксическая ошибка в ${filename}: ${error.message}`);
        }
        
        return issues;
    }

    /**
     * Проверка здоровья бэкенда
     */
    async checkBackendHealth() {
        return new Promise((resolve) => {
            const req = https.get(`${this.config.backendUrl}/api/health`, (res) => {
                if (res.statusCode === 200) {
                    console.log('✅ Бэкенд доступен');
                } else {
                    this.logError(`Бэкенд вернул статус ${res.statusCode}`);
                }
                resolve();
            });
            
            req.on('error', (error) => {
                this.logError(`Ошибка подключения к бэкенду: ${error.message}`);
                resolve();
            });
            
            req.setTimeout(10000, () => {
                this.logError('Таймаут подключения к бэкенду');
                req.destroy();
                resolve();
            });
        });
    }

    /**
     * Проверка логов ошибок
     */
    async checkErrorLogs() {
        try {
            const logDir = 'logs';
            if (fs.existsSync(logDir)) {
                const logFiles = fs.readdirSync(logDir).filter(file => file.endsWith('.log'));
                
                for (const logFile of logFiles) {
                    const logPath = path.join(logDir, logFile);
                    const stats = fs.statSync(logPath);
                    
                    // Проверяем только новые логи
                    if (stats.mtime > this.lastCheck) {
                        const content = fs.readFileSync(logPath, 'utf8');
                        const errors = content.match(/ERROR|CRITICAL|FATAL/g);
                        
                        if (errors && errors.length > 0) {
                            this.logError(`Найдено ${errors.length} ошибок в логе ${logFile}`);
                        }
                    }
                }
            }
        } catch (error) {
            this.logError(`Ошибка проверки логов: ${error.message}`);
        }
    }

    /**
     * Логирование ошибки
     */
    logError(message) {
        const error = {
            timestamp: new Date().toISOString(),
            message: message,
            severity: 'ERROR'
        };
        
        this.errorLog.push(error);
        console.error(`❌ ${error.timestamp}: ${message}`);
        
        // Ограничиваем размер лога
        if (this.errorLog.length > this.config.maxErrors) {
            this.errorLog = this.errorLog.slice(-this.config.maxErrors);
        }
        
        // Отправляем уведомление при превышении порога
        if (this.errorLog.length >= this.config.alertThreshold) {
            this.sendAlert();
        }
    }

    /**
     * Отправка уведомления
     */
    async sendAlert() {
        try {
            const alertData = {
                type: 'frontend_error_alert',
                timestamp: new Date().toISOString(),
                errorCount: this.errorLog.length,
                recentErrors: this.errorLog.slice(-5),
                message: `Обнаружено ${this.errorLog.length} ошибок фронтенда`
            };
            
            console.log('🚨 ОТПРАВКА УВЕДОМЛЕНИЯ О КРИТИЧЕСКИХ ОШИБКАХ');
            console.log(JSON.stringify(alertData, null, 2));
            
            // Здесь можно добавить отправку в Slack, email или другой сервис
            
        } catch (error) {
            console.error(`Ошибка отправки уведомления: ${error.message}`);
        }
    }

    /**
     * Запуск мониторинга
     */
    start() {
        console.log('🚀 Запуск мониторинга ошибок фронтенда...');
        console.log(`📊 Интервал проверки: ${this.config.checkInterval / 1000} секунд`);
        console.log(`⚠️  Порог уведомлений: ${this.config.alertThreshold} ошибок`);
        
        // Первая проверка
        this.checkFrontendHealth();
        
        // Периодические проверки
        setInterval(() => {
            this.checkFrontendHealth();
        }, this.config.checkInterval);
    }

    /**
     * Генерация отчета
     */
    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            totalErrors: this.errorLog.length,
            errors: this.errorLog,
            summary: {
                critical: this.errorLog.filter(e => e.severity === 'CRITICAL').length,
                errors: this.errorLog.filter(e => e.severity === 'ERROR').length,
                warnings: this.errorLog.filter(e => e.severity === 'WARNING').length
            }
        };
        
        return report;
    }
}

// Запуск мониторинга
if (require.main === module) {
    const monitor = new FrontendErrorMonitor();
    monitor.start();
    
    // Обработка сигналов завершения
    process.on('SIGINT', () => {
        console.log('\n📊 Финальный отчет:');
        console.log(JSON.stringify(monitor.generateReport(), null, 2));
        process.exit(0);
    });
    
    process.on('SIGTERM', () => {
        console.log('\n📊 Финальный отчет:');
        console.log(JSON.stringify(monitor.generateReport(), null, 2));
        process.exit(0);
    });
}

module.exports = FrontendErrorMonitor; 