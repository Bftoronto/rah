import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import traceback
import json

class StructuredLogger:
    """Структурированный логгер с детальным логированием"""
    
    def __init__(self, name: str, log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Настройка форматтера для структурированного логирования
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Консольный хендлер
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Файловый хендлер для ошибок
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        error_handler = logging.handlers.RotatingFileHandler(
            'logs/errors.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # Файловый хендлер для всех логов
        all_handler = logging.handlers.RotatingFileHandler(
            'logs/app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        all_handler.setFormatter(formatter)
        self.logger.addHandler(all_handler)
    
    def _format_context(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Форматирование контекста для логов"""
        if not context:
            return ""
        
        try:
            return f" | Context: {json.dumps(context, ensure_ascii=False, default=str)}"
        except Exception:
            return f" | Context: {str(context)}"
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Информационное сообщение"""
        context_str = self._format_context(context)
        self.logger.info(f"{message}{context_str}")
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Предупреждение"""
        context_str = self._format_context(context)
        self.logger.warning(f"{message}{context_str}")
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        """Ошибка с детальной информацией"""
        context_str = self._format_context(context)
        self.logger.error(f"{message}{context_str}", exc_info=exc_info)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Отладочное сообщение"""
        context_str = self._format_context(context)
        self.logger.debug(f"{message}{context_str}")
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = True):
        """Критическая ошибка"""
        context_str = self._format_context(context)
        self.logger.critical(f"{message}{context_str}", exc_info=exc_info)

class DatabaseLogger:
    """Специализированный логгер для операций с базой данных"""
    
    def __init__(self):
        self.logger = StructuredLogger("database")
    
    def query_start(self, query_type: str, table: str, filters: Optional[Dict] = None):
        """Логирование начала запроса"""
        context = {
            "query_type": query_type,
            "table": table,
            "filters": filters,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.debug(f"Database query started", context)
    
    def query_success(self, query_type: str, table: str, result_count: int, duration_ms: float):
        """Логирование успешного запроса"""
        context = {
            "query_type": query_type,
            "table": table,
            "result_count": result_count,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"Database query completed successfully", context)
    
    def query_error(self, query_type: str, table: str, error: Exception, sql: Optional[str] = None):
        """Логирование ошибки запроса"""
        context = {
            "query_type": query_type,
            "table": table,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "sql": sql,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.error(f"Database query failed", context)
    
    def transaction_start(self, operation: str):
        """Логирование начала транзакции"""
        context = {
            "operation": operation,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.debug(f"Database transaction started", context)
    
    def transaction_commit(self, operation: str, duration_ms: float):
        """Логирование успешной транзакции"""
        context = {
            "operation": operation,
            "duration_ms": duration_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.info(f"Database transaction committed", context)
    
    def transaction_rollback(self, operation: str, error: Exception):
        """Логирование отката транзакции"""
        context = {
            "operation": operation,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.error(f"Database transaction rolled back", context)

class SecurityLogger:
    """Специализированный логгер для событий безопасности"""
    
    def __init__(self):
        self.logger = StructuredLogger("security")
    
    def authentication_attempt(self, user_id: Optional[str], method: str, success: bool, ip: Optional[str] = None):
        """Логирование попытки аутентификации"""
        context = {
            "user_id": user_id,
            "method": method,
            "success": success,
            "ip_address": ip,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if success:
            self.logger.info(f"Authentication successful", context)
        else:
            self.logger.warning(f"Authentication failed", context)
    
    def authorization_check(self, user_id: str, resource: str, action: str, granted: bool):
        """Логирование проверки авторизации"""
        context = {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if granted:
            self.logger.debug(f"Authorization granted", context)
        else:
            self.logger.warning(f"Authorization denied", context)
    
    def data_validation_error(self, field: str, value: Any, rule: str, user_id: Optional[str] = None):
        """Логирование ошибки валидации данных"""
        context = {
            "field": field,
            "value": str(value),
            "rule": rule,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.logger.warning(f"Data validation error", context)
    
    def telegram_verification(self, telegram_id: str, success: bool, details: Optional[Dict] = None):
        """Логирование верификации Telegram"""
        context = {
            "telegram_id": telegram_id,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if success:
            self.logger.info(f"Telegram verification successful", context)
        else:
            self.logger.warning(f"Telegram verification failed", context)

class PerformanceLogger:
    """Специализированный логгер для метрик производительности"""
    
    def __init__(self):
        self.logger = StructuredLogger("performance")
    
    def api_request(self, endpoint: str, method: str, duration_ms: float, status_code: int, user_id: Optional[str] = None):
        """Логирование API запроса"""
        context = {
            "endpoint": endpoint,
            "method": method,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if duration_ms > 1000:  # Медленные запросы
            self.logger.warning(f"Slow API request detected", context)
        else:
            self.logger.debug(f"API request completed", context)
    
    def database_performance(self, operation: str, table: str, duration_ms: float, rows_affected: Optional[int] = None):
        """Логирование производительности БД"""
        context = {
            "operation": operation,
            "table": table,
            "duration_ms": duration_ms,
            "rows_affected": rows_affected,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if duration_ms > 500:  # Медленные запросы к БД
            self.logger.warning(f"Slow database operation detected", context)
        else:
            self.logger.debug(f"Database operation completed", context)
    
    def memory_usage(self, memory_mb: float, component: str):
        """Логирование использования памяти"""
        context = {
            "memory_mb": memory_mb,
            "component": component,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if memory_mb > 100:  # Высокое использование памяти
            self.logger.warning(f"High memory usage detected", context)
        else:
            self.logger.debug(f"Memory usage normal", context)

# Создаем глобальные экземпляры логгеров
db_logger = DatabaseLogger()
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()

def get_logger(name: str) -> StructuredLogger:
    """Получение структурированного логгера по имени"""
    return StructuredLogger(name)

def log_exception(logger: StructuredLogger, error: Exception, context: Optional[Dict[str, Any]] = None):
    """Централизованное логирование исключений"""
    error_context = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if context:
        error_context.update(context)
    
    logger.error(f"Exception occurred: {str(error)}", error_context, exc_info=False) 