"""
Система кэширования для оптимизации производительности
"""
import time
import json
from typing import Any, Optional, Dict, Callable
from functools import wraps
import logging
from threading import Lock

logger = logging.getLogger(__name__)

class MemoryCache:
    """Простое кэширование в памяти"""
    
    def __init__(self, default_ttl: int = 300):  # 5 минут по умолчанию
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        with self._lock:
            if key in self._cache:
                item = self._cache[key]
                if time.time() < item['expires_at']:
                    return item['value']
                else:
                    # Удаляем истекший элемент
                    del self._cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Установить значение в кэш"""
        with self._lock:
            ttl = ttl or self.default_ttl
            self._cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }
    
    def delete(self, key: str) -> None:
        """Удалить значение из кэша"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
    
    def clear(self) -> None:
        """Очистить весь кэш"""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Очистить истекшие элементы и вернуть количество удаленных"""
        current_time = time.time()
        expired_keys = []
        
        with self._lock:
            for key, item in self._cache.items():
                if current_time >= item['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику кэша"""
        with self._lock:
            current_time = time.time()
            total_items = len(self._cache)
            expired_items = sum(
                1 for item in self._cache.values() 
                if current_time >= item['expires_at']
            )
            
            return {
                'total_items': total_items,
                'expired_items': expired_items,
                'active_items': total_items - expired_items
            }

# Глобальный экземпляр кэша
cache = MemoryCache()

def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Декоратор для кэширования результатов функций"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Создаем ключ кэша
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Пытаемся получить из кэша
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Выполняем функцию и кэшируем результат
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, cached result")
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Декоратор для инвалидации кэша"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Инвалидируем кэш по паттерну
            with cache._lock:
                keys_to_delete = [
                    key for key in cache._cache.keys() 
                    if pattern in key
                ]
                for key in keys_to_delete:
                    del cache._cache[key]
            
            logger.debug(f"Invalidated cache pattern: {pattern}")
            return result
        return wrapper
    return decorator 