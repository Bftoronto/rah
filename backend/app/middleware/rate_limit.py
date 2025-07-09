"""
Rate Limiting Middleware для FastAPI
Ограничивает частоту запросов для предотвращения злоупотреблений
"""

import time
import hashlib
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
import json

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger("rate_limit")

class RateLimiter:
    """Класс для ограничения частоты запросов"""
    
    def __init__(self):
        self.redis_client = None
        self.use_redis = bool(settings.redis_url)
        
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(settings.redis_url)
                self.redis_client.ping()  # Проверяем подключение
                logger.info("Rate limiter подключен к Redis")
            except Exception as e:
                logger.warning(f"Не удалось подключиться к Redis: {e}")
                self.use_redis = False
        
        # Настройки лимитов
        self.limits = {
            "default": {"requests": 100, "window": 60},  # 100 запросов в минуту
            "auth": {"requests": 10, "window": 60},      # 10 попыток входа в минуту
            "upload": {"requests": 20, "window": 60},    # 20 загрузок в минуту
            "api": {"requests": 1000, "window": 3600},   # 1000 запросов в час
        }
    
    def get_client_ip(self, request: Request) -> str:
        """Получение IP адреса клиента"""
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    def get_user_identifier(self, request: Request) -> str:
        """Получение идентификатора пользователя для rate limiting"""
        # Сначала пытаемся получить из JWT токена
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from ..utils.jwt_auth import jwt_auth
                token = auth_header.split(" ")[1]
                payload = jwt_auth.verify_token(token, "access")
                return f"user:{payload.get('user_id')}"
            except:
                pass
        
        # Если нет токена, используем IP
        return f"ip:{self.get_client_ip(request)}"
    
    def get_limit_key(self, identifier: str, endpoint: str) -> str:
        """Генерация ключа для Redis"""
        return f"rate_limit:{identifier}:{endpoint}"
    
    def check_rate_limit(self, identifier: str, endpoint: str) -> Tuple[bool, Dict]:
        """
        Проверка rate limit
        
        Args:
            identifier: Идентификатор пользователя/IP
            endpoint: Эндпоинт
            
        Returns:
            Tuple[bool, Dict]: (разрешено, информация о лимитах)
        """
        limit_config = self.limits.get(endpoint, self.limits["default"])
        key = self.get_limit_key(identifier, endpoint)
        current_time = int(time.time())
        
        if self.use_redis and self.redis_client:
            return self._check_redis_limit(key, current_time, limit_config)
        else:
            return self._check_memory_limit(key, current_time, limit_config)
    
    def _check_redis_limit(self, key: str, current_time: int, limit_config: Dict) -> Tuple[bool, Dict]:
        """Проверка лимита через Redis"""
        try:
            # Получаем текущие запросы
            requests_data = self.redis_client.get(key)
            
            if requests_data:
                requests = json.loads(requests_data)
            else:
                requests = []
            
            # Удаляем старые запросы
            window_start = current_time - limit_config["window"]
            requests = [req for req in requests if req > window_start]
            
            # Проверяем лимит
            if len(requests) >= limit_config["requests"]:
                return False, {
                    "limit": limit_config["requests"],
                    "window": limit_config["window"],
                    "remaining": 0,
                    "reset_time": requests[0] + limit_config["window"] if requests else current_time
                }
            
            # Добавляем новый запрос
            requests.append(current_time)
            self.redis_client.setex(
                key, 
                limit_config["window"], 
                json.dumps(requests)
            )
            
            return True, {
                "limit": limit_config["requests"],
                "window": limit_config["window"],
                "remaining": limit_config["requests"] - len(requests),
                "reset_time": current_time + limit_config["window"]
            }
            
        except Exception as e:
            logger.error(f"Ошибка Redis rate limiting: {e}")
            # В случае ошибки Redis разрешаем запрос
            return True, {"error": "Redis недоступен"}
    
    def _check_memory_limit(self, key: str, current_time: int, limit_config: Dict) -> Tuple[bool, Dict]:
        """Проверка лимита в памяти (fallback)"""
        # Простая реализация в памяти
        # В продакшене лучше использовать Redis
        return True, {"note": "Используется in-memory rate limiting"}

# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware для ограничения частоты запросов
    
    Args:
        request: HTTP запрос
        call_next: Следующий обработчик
        
    Returns:
        Response: HTTP ответ
    """
    try:
        # Определяем тип эндпоинта
        path = request.url.path
        endpoint = "default"
        
        if path.startswith("/api/auth"):
            endpoint = "auth"
        elif path.startswith("/api/upload"):
            endpoint = "upload"
        elif path.startswith("/api/"):
            endpoint = "api"
        
        # Получаем идентификатор пользователя
        identifier = rate_limiter.get_user_identifier(request)
        
        # Проверяем rate limit
        allowed, limit_info = rate_limiter.check_rate_limit(identifier, endpoint)
        
        if not allowed:
            logger.warning(f"Rate limit превышен для {identifier} на {endpoint}")
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "detail": "Превышен лимит запросов",
                    "retry_after": limit_info.get("reset_time", 60),
                    "limit_info": limit_info
                },
                headers={
                    "X-RateLimit-Limit": str(limit_info.get("limit", 0)),
                    "X-RateLimit-Remaining": str(limit_info.get("remaining", 0)),
                    "X-RateLimit-Reset": str(limit_info.get("reset_time", 0)),
                    "Retry-After": str(limit_info.get("reset_time", 60))
                }
            )
        
        # Добавляем информацию о лимитах в заголовки
        response = await call_next(request)
        
        response.headers["X-RateLimit-Limit"] = str(limit_info.get("limit", 0))
        response.headers["X-RateLimit-Remaining"] = str(limit_info.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(limit_info.get("reset_time", 0))
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка rate limiting middleware: {e}")
        # В случае ошибки пропускаем запрос
        return await call_next(request) 