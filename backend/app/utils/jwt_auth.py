"""
JWT авторизация для FastAPI приложения
Реализует безопасную систему токенов с refresh механизмом
"""

import jwt
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import secrets
import hashlib

from ..database import get_db
from ..models.user import User
from ..config.settings import settings
from ..utils.logger import get_logger
from ..utils.security import hash_password, verify_password

logger = get_logger("jwt_auth")
security = HTTPBearer()

class JWTAuth:
    """Класс для работы с JWT токенами"""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Создание access токена
        
        Args:
            data: Данные для включения в токен
            expires_delta: Время жизни токена
            
        Returns:
            str: JWT токен
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"Создан access токен для пользователя {data.get('user_id')}")
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Создание refresh токена
        
        Args:
            data: Данные для включения в токен
            
        Returns:
            str: JWT refresh токен
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire, 
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # Уникальный идентификатор токена
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        logger.info(f"Создан refresh токен для пользователя {data.get('user_id')}")
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Верификация JWT токена с усиленной безопасностью и детальной обработкой ошибок
        """
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен не предоставлен"
            )
        
        # Проверка длины токена (базовая защита от вредоносных данных)
        if len(token) > 2048:
            logger.warning("Слишком длинный токен")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный формат токена"
            )
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Проверка типа токена
            if payload.get("type") != token_type:
                logger.warning(f"Попытка использовать токен не того типа: {payload.get('type')} вместо {token_type}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный тип токена"
                )
            
            # Проверка времени жизни
            exp = payload.get("exp")
            if exp is None:
                logger.error("Токен не содержит время жизни (exp)")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Токен не содержит время жизни"
                )
            
            if datetime.utcnow() > datetime.fromtimestamp(exp):
                logger.warning("Токен истёк")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Токен истёк"
                )
            
            # Проверка обязательных полей
            required_fields = ["user_id", "telegram_id", "iat"]
            missing_fields = [field for field in required_fields if field not in payload]
            if missing_fields:
                logger.error(f"Отсутствуют обязательные поля в токене: {missing_fields}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Токен содержит неполные данные"
                )
            
            # Принцип наименьших привилегий: только нужные поля
            allowed_fields = {"user_id", "telegram_id", "exp", "type", "iat", "jti"}
            filtered_payload = {k: v for k, v in payload.items() if k in allowed_fields}
            
            return filtered_payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Истёкшая подпись токена")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Истёкшая подпись токена"
            )
        except jwt.InvalidTokenError as e:
            logger.error(f"Невалидный токен: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невалидный токен"
            )
        except jwt.DecodeError:
            logger.error("Ошибка декодирования токена")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Поврежденный токен"
            )
        except Exception as e:
            logger.error(f"Неожиданная ошибка при верификации токена: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ошибка верификации токена"
            )
    
    def create_token_pair(self, user_id: int, telegram_id: str) -> Dict[str, str]:
        """
        Создание пары токенов (access + refresh)
        
        Args:
            user_id: ID пользователя
            telegram_id: Telegram ID пользователя
            
        Returns:
            Dict[str, str]: Пара токенов
        """
        data = {
            "user_id": user_id,
            "telegram_id": telegram_id,
            "iat": datetime.utcnow()
        }
        
        access_token = self.create_access_token(data)
        refresh_token = self.create_refresh_token(data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

# Глобальный экземпляр JWT авторизации
jwt_auth = JWTAuth()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Получение текущего пользователя по JWT токену
    
    Args:
        credentials: JWT токен из заголовка
        db: Сессия базы данных
        
    Returns:
        User: Текущий пользователь
        
    Raises:
        HTTPException: При ошибке авторизации
    """
    try:
        # Верифицируем access токен
        payload = jwt_auth.verify_token(credentials.credentials, "access")
        user_id = payload.get("user_id")
        telegram_id = payload.get("telegram_id")
        
        if not user_id or not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные данные токена"
            )
        
        # Получаем пользователя из базы данных
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"Пользователь не найден по ID: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        # Проверяем, что Telegram ID совпадает
        if user.telegram_id != telegram_id:
            logger.warning(f"Несоответствие Telegram ID для пользователя {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные данные авторизации"
            )
        
        # Обновляем время последнего доступа
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Успешная авторизация пользователя {user_id}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения текущего пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка авторизации"
        )

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Получение текущего пользователя (опционально)
    Возвращает None если токен отсутствует или неверен
    
    Args:
        credentials: JWT токен из заголовка (опционально)
        db: Сессия базы данных
        
    Returns:
        Optional[User]: Текущий пользователь или None
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

def require_auth(user: User = Depends(get_current_user)) -> User:
    """
    Зависимость для обязательной авторизации
    
    Args:
        user: Текущий пользователь
        
    Returns:
        User: Авторизованный пользователь
    """
    return user

def require_driver(user: User = Depends(get_current_user)) -> User:
    """
    Зависимость для водителей
    
    Args:
        user: Текущий пользователь
        
    Returns:
        User: Пользователь-водитель
        
    Raises:
        HTTPException: Если пользователь не водитель
    """
    if not user.is_driver:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права водителя"
        )
    return user

def require_verified_user(user: User = Depends(get_current_user)) -> User:
    """
    Зависимость для верифицированных пользователей
    
    Args:
        user: Текущий пользователь
        
    Returns:
        User: Верифицированный пользователь
        
    Raises:
        HTTPException: Если пользователь не верифицирован
    """
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуется верификация аккаунта"
        )
    return user 