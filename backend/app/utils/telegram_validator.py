"""
Централизованный валидатор Telegram данных
"""
import hashlib
import hmac
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TelegramValidator:
    """Централизованный валидатор Telegram данных"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA')
    
    def verify_webapp_data(self, data: Dict[str, Any]) -> bool:
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
            
            if not self.bot_token:
                logger.error("Отсутствует TELEGRAM_BOT_TOKEN в переменных окружения")
                return False
            
            # Создаем секретный ключ из токена бота
            secret_key = hmac.new(
                key=b"WebAppData",
                msg=self.bot_token.encode(),
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
            
            # Сравниваем подписи
            is_valid = calculated_hash == hash_str
            
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
    
    def verify_login_data(self, data: Dict[str, str]) -> bool:
        """
        Верификация данных Telegram Login
        """
        try:
            auth_data = data.copy()
            hash_ = auth_data.pop('hash')
            data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(auth_data.items())])
            secret_key = hashlib.sha256(self.bot_token.encode()).digest()
            hmac_string = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
            return hmac_string == hash_
        except Exception as e:
            logger.error(f"Ошибка верификации Telegram Login: {str(e)}")
            return False
    
    def extract_user_data(self, telegram_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Извлечение данных пользователя из Telegram
        """
        return {
            'id': telegram_user.get('id'),
            'username': telegram_user.get('username'),
            'first_name': telegram_user.get('first_name'),
            'last_name': telegram_user.get('last_name'),
            'language_code': telegram_user.get('language_code'),
            'is_premium': telegram_user.get('is_premium', False),
            'photo_url': telegram_user.get('photo_url')
        }

# Глобальный экземпляр валидатора
telegram_validator = TelegramValidator() 