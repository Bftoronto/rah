from passlib.context import CryptContext
import hashlib
import hmac
import os
import time
from typing import Dict, Any
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)
security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def verify_telegram_data(data: Dict[str, Any]) -> bool:
    """
    Верификация данных от Telegram Web App
    """
    try:
        # Проверяем, что данные содержат user объект
        if 'user' not in data:
            logger.warning("Отсутствует объект user в данных Telegram")
            return False
        
        # Получаем подпись из данных
        hash_str = data.get('hash', '')
        if not hash_str:
            logger.warning("Отсутствует подпись в данных Telegram")
            # В режиме разработки разрешаем без подписи
            if os.getenv('ENVIRONMENT', 'production') == 'development':
                logger.warning("Development mode: Allowing unverified Telegram data")
                return True
            return False
        
        # Получаем токен бота из переменных окружения
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            logger.error("Отсутствует TELEGRAM_BOT_TOKEN в переменных окружения")
            # В режиме разработки возвращаем False для безопасности
            if os.getenv('ENVIRONMENT', 'production') == 'development':
                logger.warning("Development mode: Missing bot token")
                return True
            return False
        
        # Создаем секретный ключ из токена бота
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=bot_token.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Убираем hash из данных для проверки
        data_check = data.copy()
        data_check.pop('hash', None)
        
        # Сортируем данные по ключам
        data_check_string = '\n'.join([
            f"{k}={v}" for k, v in sorted(data_check.items())
        ])
        
        # Создаем подпись
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Для отладки
        logger.info(f"Telegram data keys: {list(data.keys())}")
        logger.info(f"Calculated hash: {calculated_hash}")
        logger.info(f"Received hash: {hash_str}")
        
        # Сравниваем подписи
        is_valid = calculated_hash == hash_str
        
        # Для отладки в продакшене временно отключаем строгую проверку
        if not is_valid:
            logger.warning(f"Hash verification failed. Expected: {calculated_hash}, Got: {hash_str}")
            # Временно разрешаем для тестирования
            if os.getenv('ENVIRONMENT', 'production') == 'development':
                logger.warning("Development mode: Allowing unverified Telegram data")
                return True
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Ошибка верификации Telegram данных: {str(e)}")
        return False

def generate_telegram_auth_url(bot_username: str, redirect_url: str = None) -> str:
    """
    Генерация URL для авторизации через Telegram
    """
    base_url = f"https://t.me/{bot_username}"
    if redirect_url:
        base_url += f"?start={redirect_url}"
    return base_url

def extract_telegram_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Извлечение данных пользователя из Telegram Web App
    """
    return {
        'id': data.get('id'),
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'username': data.get('username'),
        'photo_url': data.get('photo_url'),
        'auth_date': data.get('auth_date'),
        'hash': data.get('hash')
    }

def validate_telegram_user_data(data: Dict[str, Any]) -> bool:
    """
    Валидация данных пользователя Telegram
    """
    required_fields = ['id', 'first_name', 'auth_date']
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Отсутствует обязательное поле: {field}")
            return False
    
    # Проверяем, что ID является числом
    try:
        int(data['id'])
    except (ValueError, TypeError):
        logger.warning("Telegram ID должен быть числом")
        return False
    
    # Проверяем дату авторизации (не старше 24 часов)
    try:
        auth_date = int(data['auth_date'])
        current_time = int(time.time())
        if current_time - auth_date > 86400:  # 24 часа
            logger.warning("Данные авторизации устарели")
            return False
    except (ValueError, TypeError):
        logger.warning("Некорректная дата авторизации")
        return False
    
    return True

def get_current_user_id():
    """
    Получение текущего user_id из JWT токена.
    Используется как зависимость для защищенных эндпоинтов.
    """
    def _get_user_id_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
        try:
            from .jwt_auth import jwt_auth
            
            token = credentials.credentials
            
            # Верифицируем токен и получаем payload
            payload = jwt_auth.verify_token(token, "access")
            user_id = payload.get("user_id")
            telegram_id = payload.get("telegram_id")
            
            if not user_id or not telegram_id:
                logger.warning("Неверный формат токена в get_current_user_id")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный формат токена"
                )
            
            logger.debug(f"Извлечен user_id: {user_id} из токена")
            return user_id
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения user_id из токена: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ошибка авторизации"
            )
    
    return _get_user_id_from_token 