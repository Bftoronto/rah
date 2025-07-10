"""
Система кэширования для FastAPI приложения
Поддерживает Redis и in-memory кэширование с умной инвалидацией
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict, List, Union, Set
from functools import wraps
import redis
import pickle
from datetime import datetime, timedelta

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger("cache_manager")

class CacheDependency:
    """Класс для управления зависимостями кэша"""
    
    def __init__(self, entity_type: str, entity_id: Optional[int] = None):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.key = f"{entity_type}:{entity_id}" if entity_id else entity_type
    
    def __str__(self):
        return self.key

class CacheInvalidationManager:
    """Менеджер умной инвалидации кэша"""
    
    def __init__(self):
        self.dependencies: Dict[str, Set[str]] = {}  # entity -> cache_keys
        self.reverse_deps: Dict[str, Set[str]] = {}  # cache_key -> entities
        self.invalidation_queue: List[Dict[str, Any]] = []
    
    def add_dependency(self, cache_key: str, dependencies: List[CacheDependency]):
        """Добавляет зависимости для ключа кэша"""
        for dep in dependencies:
            dep_key = str(dep)
            if dep_key not in self.dependencies:
                self.dependencies[dep_key] = set()
            self.dependencies[dep_key].add(cache_key)
            
            if cache_key not in self.reverse_deps:
                self.reverse_deps[cache_key] = set()
            self.reverse_deps[cache_key].add(dep_key)
    
    def invalidate_entity(self, entity_type: str, entity_id: Optional[int] = None):
        """Инвалидирует кэш для конкретной сущности"""
        dep_key = f"{entity_type}:{entity_id}" if entity_id else entity_type
        
        if dep_key in self.dependencies:
            cache_keys = self.dependencies[dep_key].copy()
            for cache_key in cache_keys:
                self._invalidate_cache_key(cache_key)
                # Удаляем зависимость
                self.dependencies[dep_key].discard(cache_key)
                if cache_key in self.reverse_deps:
                    self.reverse_deps[cache_key].discard(dep_key)
    
    def invalidate_pattern(self, pattern: str):
        """Инвалидирует кэш по паттерну"""
        matching_keys = []
        for cache_key in self.reverse_deps.keys():
            if pattern in cache_key:
                matching_keys.append(cache_key)
        
        for cache_key in matching_keys:
            self._invalidate_cache_key(cache_key)
    
    def _invalidate_cache_key(self, cache_key: str):
        """Инвалидирует конкретный ключ кэша"""
        # Добавляем в очередь инвалидации
        self.invalidation_queue.append({
            'key': cache_key,
            'timestamp': datetime.now(),
            'reason': 'dependency_invalidation'
        })
        
        # Очищаем старые записи из очереди (старше 1 часа)
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.invalidation_queue = [
            item for item in self.invalidation_queue 
            if item['timestamp'] > cutoff_time
        ]
    
    def get_invalidation_stats(self) -> Dict[str, Any]:
        """Получает статистику инвалидации"""
        return {
            'total_dependencies': len(self.dependencies),
            'total_cache_keys': len(self.reverse_deps),
            'recent_invalidations': len(self.invalidation_queue),
            'dependency_types': list(set(dep.split(':')[0] for dep in self.dependencies.keys()))
        }

class CacheManager:
    """Менеджер кэширования с поддержкой Redis и умной инвалидацией"""
    
    def __init__(self):
        self.redis_client = None
        self.use_redis = bool(settings.redis_url)
        self.memory_cache = {}  # In-memory fallback
        self.default_ttl = settings.cache_ttl
        self.invalidation_manager = CacheInvalidationManager()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'invalidations': 0
        }
        
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
                result = self._get_from_redis(key, default)
            else:
                result = self._get_from_memory(key, default)
            
            if result is not default:
                self.stats['hits'] += 1
            else:
                self.stats['misses'] += 1
            
            return result
        except Exception as e:
            logger.error(f"Ошибка получения из кэша: {e}")
            self.stats['misses'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, dependencies: Optional[List[CacheDependency]] = None) -> bool:
        """
        Установка значения в кэш
        
        Args:
            key: Ключ кэша
            value: Значение для кэширования
            ttl: Время жизни в секундах
            dependencies: Список зависимостей для умной инвалидации
            
        Returns:
            bool: Успешность операции
        """
        try:
            if self.use_redis and self.redis_client:
                success = self._set_to_redis(key, value, ttl)
            else:
                success = self._set_to_memory(key, value, ttl)
            
            if success:
                self.stats['sets'] += 1
                # Добавляем зависимости для умной инвалидации
                if dependencies:
                    self.invalidation_manager.add_dependency(key, dependencies)
            
            return success
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
                success = self._delete_from_redis(key)
            else:
                success = self._delete_from_memory(key)
            
            if success:
                self.stats['deletes'] += 1
            
            return success
        except Exception as e:
            logger.error(f"Ошибка удаления из кэша: {e}")
            return False
    
    def invalidate_entity(self, entity_type: str, entity_id: Optional[int] = None):
        """
        Умная инвалидация кэша для сущности
        
        Args:
            entity_type: Тип сущности (user, ride, rating, etc.)
            entity_id: ID сущности (опционально)
        """
        try:
            self.invalidation_manager.invalidate_entity(entity_type, entity_id)
            self.stats['invalidations'] += 1
            logger.info(f"Инвалидирован кэш для {entity_type}:{entity_id}")
        except Exception as e:
            logger.error(f"Ошибка инвалидации кэша: {e}")
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Инвалидация кэша по паттерну
        
        Args:
            pattern: Паттерн ключей
            
        Returns:
            int: Количество удаленных ключей
        """
        try:
            count = self.clear_pattern(pattern)
            self.invalidation_manager.invalidate_pattern(pattern)
            self.stats['invalidations'] += 1
            return count
        except Exception as e:
            logger.error(f"Ошибка инвалидации по паттерну: {e}")
            return 0
    
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
    
    def get_stats(self) -> Dict[str, Any]:
        """Получает статистику кэша"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests,
            'invalidation_stats': self.invalidation_manager.get_invalidation_stats()
        }
    
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
            deleted_count = 0
            keys_to_delete = []
            
            for key in self.memory_cache.keys():
                if pattern in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.memory_cache[key]
                deleted_count += 1
            
            return deleted_count
        except Exception as e:
            logger.error(f"Ошибка очистки по паттерну в памяти: {e}")
            return 0
    
    def _cleanup_memory_cache(self):
        """Очистка истекших записей в памяти"""
        try:
            current_time = time.time()
            keys_to_delete = []
            
            for key, (_, expiry) in self.memory_cache.items():
                if expiry and current_time > expiry:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.memory_cache[key]
        except Exception as e:
            logger.error(f"Ошибка очистки памяти: {e}")

# Глобальный экземпляр кэш-менеджера
cache_manager = CacheManager()

def cached(prefix: str, ttl: Optional[int] = None, dependencies: Optional[List[CacheDependency]] = None):
    """
    Декоратор для кэширования функций
    
    Args:
        prefix: Префикс ключа кэша
        ttl: Время жизни в секундах
        dependencies: Список зависимостей для умной инвалидации
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Пытаемся получить из кэша
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Выполняем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            cache_manager.set(cache_key, result, ttl, dependencies)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Генерируем ключ кэша
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Пытаемся получить из кэша
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Выполняем функцию
            result = func(*args, **kwargs)
            
            # Сохраняем в кэш
            cache_manager.set(cache_key, result, ttl, dependencies)
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def invalidate_cache(prefix: str):
    """
    Декоратор для инвалидации кэша после выполнения функции
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            cache_manager.invalidate_pattern(prefix)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_manager.invalidate_pattern(prefix)
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator 