"""
Система кэширования для FastAPI приложения
Поддерживает Redis и in-memory кэширование
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict, List, Union
from functools import wraps
import redis
import pickle

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger("cache_manager")

class CacheManager:
    """Менеджер кэширования с поддержкой Redis"""
    
    def __init__(self):
        self.redis_client = None
        self.use_redis = bool(settings.redis_url)
        self.memory_cache = {}  # In-memory fallback
        self.default_ttl = settings.cache_ttl
        
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(settings.redis_url)
                self.redis_client.ping()
                logger.info("Cache manager подключен к Redis")
            except Exception as e:
                logger.warning(f"Не удалось подключиться к Redis: {e}")
                self.use_redis = False
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Генерация ключа кэша"""
        # Создаем строку из аргументов
        key_parts = [prefix]
        
        # Добавляем позиционные аргументы
        for arg in args:
            key_parts.append(str(arg))
        
        # Добавляем именованные аргументы
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        # Создаем хеш
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Получение значения из кэша
        
        Args:
            key: Ключ кэша
            default: Значение по умолчанию
            
        Returns:
            Any: Значение из кэша или default
        """
        try:
            if self.use_redis and self.redis_client:
                return self._get_from_redis(key, default)
            else:
                return self._get_from_memory(key, default)
        except Exception as e:
            logger.error(f"Ошибка получения из кэша: {e}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Установка значения в кэш
        
        Args:
            key: Ключ кэша
            value: Значение для кэширования
            ttl: Время жизни в секундах
            
        Returns:
            bool: Успешность операции
        """
        try:
            if self.use_redis and self.redis_client:
                return self._set_to_redis(key, value, ttl)
            else:
                return self._set_to_memory(key, value, ttl)
        except Exception as e:
            logger.error(f"Ошибка установки в кэш: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Удаление значения из кэша
        
        Args:
            key: Ключ кэша
            
        Returns:
            bool: Успешность операции
        """
        try:
            if self.use_redis and self.redis_client:
                return self._delete_from_redis(key)
            else:
                return self._delete_from_memory(key)
        except Exception as e:
            logger.error(f"Ошибка удаления из кэша: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Очистка кэша по паттерну
        
        Args:
            pattern: Паттерн ключей
            
        Returns:
            int: Количество удаленных ключей
        """
        try:
            if self.use_redis and self.redis_client:
                return self._clear_pattern_redis(pattern)
            else:
                return self._clear_pattern_memory(pattern)
        except Exception as e:
            logger.error(f"Ошибка очистки кэша по паттерну: {e}")
            return 0
    
    def _get_from_redis(self, key: str, default: Any) -> Any:
        """Получение из Redis"""
        try:
            data = self.redis_client.get(key)
            if data:
                return pickle.loads(data)
            return default
        except Exception as e:
            logger.error(f"Ошибка получения из Redis: {e}")
            return default
    
    def _set_to_redis(self, key: str, value: Any, ttl: Optional[int]) -> bool:
        """Установка в Redis"""
        try:
            data = pickle.dumps(value)
            if ttl:
                self.redis_client.setex(key, ttl, data)
            else:
                self.redis_client.setex(key, self.default_ttl, data)
            return True
        except Exception as e:
            logger.error(f"Ошибка установки в Redis: {e}")
            return False
    
    def _delete_from_redis(self, key: str) -> bool:
        """Удаление из Redis"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Ошибка удаления из Redis: {e}")
            return False
    
    def _clear_pattern_redis(self, pattern: str) -> int:
        """Очистка по паттерну в Redis"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Ошибка очистки по паттерну в Redis: {e}")
            return 0
    
    def _get_from_memory(self, key: str, default: Any) -> Any:
        """Получение из памяти"""
        if key in self.memory_cache:
            data, expiry = self.memory_cache[key]
            if expiry is None or time.time() < expiry:
                return data
            else:
                del self.memory_cache[key]
        return default
    
    def _set_to_memory(self, key: str, value: Any, ttl: Optional[int]) -> bool:
        """Установка в память"""
        try:
            expiry = None
            if ttl:
                expiry = time.time() + ttl
            elif self.default_ttl:
                expiry = time.time() + self.default_ttl
            
            self.memory_cache[key] = (value, expiry)
            
            # Очищаем истекшие записи
            self._cleanup_memory_cache()
            
            return True
        except Exception as e:
            logger.error(f"Ошибка установки в память: {e}")
            return False
    
    def _delete_from_memory(self, key: str) -> bool:
        """Удаление из памяти"""
        try:
            if key in self.memory_cache:
                del self.memory_cache[key]
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка удаления из памяти: {e}")
            return False
    
    def _clear_pattern_memory(self, pattern: str) -> int:
        """Очистка по паттерну в памяти"""
        try:
            count = 0
            keys_to_delete = []
            
            for key in self.memory_cache.keys():
                if pattern in key:  # Простая проверка на вхождение
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.memory_cache[key]
                count += 1
            
            return count
        except Exception as e:
            logger.error(f"Ошибка очистки по паттерну в памяти: {e}")
            return 0
    
    def _cleanup_memory_cache(self):
        """Очистка истекших записей в памяти"""
        try:
            current_time = time.time()
            keys_to_delete = []
            
            for key, (value, expiry) in self.memory_cache.items():
                if expiry and current_time > expiry:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.memory_cache[key]
                
        except Exception as e:
            logger.error(f"Ошибка очистки памяти: {e}")

# Глобальный экземпляр cache manager
cache_manager = CacheManager()

def cached(prefix: str, ttl: Optional[int] = None):
    """
    Декоратор для кэширования результатов функций
    
    Args:
        prefix: Префикс для ключа кэша
        ttl: Время жизни кэша в секундах
        
    Returns:
        Декоратор функции
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Пытаемся получить из кэша
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Кэш hit для {func.__name__}")
                return cached_result
            
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Кэш miss для {func.__name__}, сохранено")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Пытаемся получить из кэша
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Кэш hit для {func.__name__}")
                return cached_result
            
            # Выполняем функцию
            result = func(*args, **kwargs)
            
            # Сохраняем в кэш
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Кэш miss для {func.__name__}, сохранено")
            
            return result
        
        # Возвращаем асинхронную или синхронную версию
        if func.__code__.co_flags & 0x80:  # Проверяем, является ли функция асинхронной
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def invalidate_cache(prefix: str):
    """
    Декоратор для инвалидации кэша
    
    Args:
        prefix: Префикс для очистки кэша
        
    Returns:
        Декоратор функции
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Очищаем кэш по паттерну
            pattern = f"{prefix}:*"
            deleted_count = cache_manager.clear_pattern(pattern)
            logger.debug(f"Инвалидирован кэш для {func.__name__}, удалено {deleted_count} записей")
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Очищаем кэш по паттерну
            pattern = f"{prefix}:*"
            deleted_count = cache_manager.clear_pattern(pattern)
            logger.debug(f"Инвалидирован кэш для {func.__name__}, удалено {deleted_count} записей")
            
            return result
        
        # Возвращаем асинхронную или синхронную версию
        if func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator 