from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import json
import hashlib
from datetime import datetime, timedelta
import logging

from ..database import get_db
from ..utils.jwt_auth import get_current_user
from ..models.user import User
from ..schemas.responses import create_success_response, create_error_response
from ..utils.logger import get_logger

logger = get_logger("cache_api")
router = APIRouter()

# In-memory кэш (в продакшене использовать Redis)
cache_store = {}

class CacheManager:
    """Менеджер кэширования для синхронизации с фронтендом"""
    
    def __init__(self):
        self.cache = cache_store
        self.default_ttl = 300  # 5 минут
    
    def get_cache_key(self, user_id: int, endpoint: str, params: Dict = None) -> str:
        """Генерирует ключ кэша"""
        key_data = {
            'user_id': user_id,
            'endpoint': endpoint,
            'params': params or {}
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def get(self, user_id: int, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Получает данные из кэша"""
        key = self.get_cache_key(user_id, endpoint, params)
        cached_data = self.cache.get(key)
        
        if cached_data and datetime.now() < cached_data['expires_at']:
            logger.info(f"Кэш hit для пользователя {user_id}, endpoint: {endpoint}")
            return cached_data['data']
        
        if cached_data:
            # Удаляем устаревшие данные
            del self.cache[key]
            logger.info(f"Кэш expired для пользователя {user_id}, endpoint: {endpoint}")
        
        return None
    
    def set(self, user_id: int, endpoint: str, data: Dict, ttl: int = None, params: Dict = None):
        """Сохраняет данные в кэш"""
        key = self.get_cache_key(user_id, endpoint, params)
        expires_at = datetime.now() + timedelta(seconds=ttl or self.default_ttl)
        
        self.cache[key] = {
            'data': data,
            'expires_at': expires_at,
            'created_at': datetime.now(),
            'user_id': user_id,
            'endpoint': endpoint
        }
        
        logger.info(f"Кэш set для пользователя {user_id}, endpoint: {endpoint}, TTL: {ttl}s")
    
    def invalidate(self, user_id: int, pattern: str = None):
        """Инвалидирует кэш пользователя"""
        keys_to_remove = []
        
        for key, value in self.cache.items():
            if value['user_id'] == user_id:
                if pattern is None or pattern in value['endpoint']:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        logger.info(f"Инвалидирован кэш для пользователя {user_id}, паттерн: {pattern}, удалено: {len(keys_to_remove)} записей")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получает статистику кэша"""
        total_entries = len(self.cache)
        expired_entries = 0
        user_stats = {}
        
        for key, value in self.cache.items():
            if datetime.now() >= value['expires_at']:
                expired_entries += 1
            
            user_id = value['user_id']
            if user_id not in user_stats:
                user_stats[user_id] = 0
            user_stats[user_id] += 1
        
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'users_count': len(user_stats),
            'user_stats': user_stats
        }

# Глобальный экземпляр менеджера кэша
cache_manager = CacheManager()

@router.get('/stats', response_model=dict)
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """Получение статистики кэша"""
    try:
        stats = cache_manager.get_stats()
        return create_success_response(
            data=stats,
            message="Статистика кэша получена"
        )
    except Exception as e:
        logger.error(f"Ошибка получения статистики кэша: {e}")
        return create_error_response(
            message="Ошибка получения статистики кэша",
            error_code="CACHE_STATS_ERROR"
        )

@router.post('/invalidate', response_model=dict)
async def invalidate_cache(
    pattern: str = None,
    current_user: User = Depends(get_current_user)
):
    """Инвалидация кэша пользователя"""
    try:
        cache_manager.invalidate(current_user.id, pattern)
        return create_success_response(
            message="Кэш успешно инвалидирован"
        )
    except Exception as e:
        logger.error(f"Ошибка инвалидации кэша: {e}")
        return create_error_response(
            message="Ошибка инвалидации кэша",
            error_code="CACHE_INVALIDATE_ERROR"
        )

@router.delete('/clear', response_model=dict)
async def clear_all_cache(current_user: User = Depends(get_current_user)):
    """Очистка всего кэша пользователя"""
    try:
        cache_manager.invalidate(current_user.id)
        return create_success_response(
            message="Весь кэш пользователя очищен"
        )
    except Exception as e:
        logger.error(f"Ошибка очистки кэша: {e}")
        return create_error_response(
            message="Ошибка очистки кэша",
            error_code="CACHE_CLEAR_ERROR"
        ) 