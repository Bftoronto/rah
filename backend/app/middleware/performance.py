import time
import os
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ..utils.logger import performance_logger, get_logger

logger = get_logger("performance_middleware")

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware для мониторинга производительности API"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Получаем информацию о запросе
        method = request.method
        url = str(request.url)
        user_id = None
        
        # Пытаемся получить user_id из заголовков или параметров
        try:
            # Проверяем заголовки авторизации
            auth_header = request.headers.get("authorization")
            if auth_header:
                # Здесь можно добавить логику извлечения user_id из токена
                pass
            
            # Проверяем параметры запроса
            if "user_id" in request.query_params:
                user_id = request.query_params.get("user_id")
        except Exception as e:
            logger.debug(f"Не удалось получить user_id: {str(e)}")
        
        # Выполняем запрос
        try:
            response = await call_next(request)
            
            # Рассчитываем время выполнения
            duration_ms = (time.time() - start_time) * 1000
            
            # Логируем производительность
            performance_logger.api_request(
                endpoint=url,
                method=method,
                duration_ms=duration_ms,
                status_code=response.status_code,
                user_id=user_id
            )
            
            # Добавляем заголовки с метриками
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            response.headers["X-Request-ID"] = str(int(start_time * 1000))
            
            return response
            
        except Exception as e:
            # Рассчитываем время до ошибки
            duration_ms = (time.time() - start_time) * 1000
            
            # Логируем ошибку
            performance_logger.api_request(
                endpoint=url,
                method=method,
                duration_ms=duration_ms,
                status_code=500,
                user_id=user_id
            )
            
            logger.error(f"Ошибка в middleware производительности: {str(e)}")
            raise

class MemoryMonitor:
    """Монитор использования памяти (без psutil)"""
    
    @staticmethod
    def get_memory_usage() -> float:
        """Получить текущее использование памяти в МБ"""
        try:
            # Альтернативный способ получения информации о памяти
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        memory_kb = int(line.split()[1])
                        return memory_kb / 1024  # Конвертируем в МБ
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка получения информации о памяти: {str(e)}")
            return 0.0
    
    @staticmethod
    def log_memory_usage(component: str):
        """Логировать использование памяти для компонента"""
        try:
            memory_mb = MemoryMonitor.get_memory_usage()
            performance_logger.memory_usage(memory_mb, component)
        except Exception as e:
            logger.error(f"Ошибка логирования использования памяти: {str(e)}")

class DatabasePerformanceMonitor:
    """Монитор производительности базы данных"""
    
    def __init__(self):
        self.query_times = {}
    
    def start_query(self, query_type: str, table: str):
        """Начать отслеживание запроса"""
        query_key = f"{query_type}_{table}_{int(time.time() * 1000)}"
        self.query_times[query_key] = {
            "type": query_type,
            "table": table,
            "start_time": time.time()
        }
        return query_key
    
    def end_query(self, query_key: str, result_count: int = 0):
        """Завершить отслеживание запроса"""
        if query_key in self.query_times:
            query_info = self.query_times[query_key]
            duration_ms = (time.time() - query_info["start_time"]) * 1000
            
            performance_logger.database_performance(
                operation=query_info["type"],
                table=query_info["table"],
                duration_ms=duration_ms,
                rows_affected=result_count
            )
            
            del self.query_times[query_key]
    
    def get_active_queries(self) -> dict:
        """Получить активные запросы"""
        return self.query_times.copy()

# Глобальный экземпляр монитора БД
db_monitor = DatabasePerformanceMonitor() 