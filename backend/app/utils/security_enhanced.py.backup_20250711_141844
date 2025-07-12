"""
Объединенный модуль безопасности с улучшенной обработкой ошибок
Включает в себя все необходимые функции для обеспечения безопасности приложения
"""

import hashlib
import hmac
import secrets
import re
import time
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from pydantic import ValidationError

from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger("security")

class SecurityError(Exception):
    """Базовый класс для ошибок безопасности"""
    pass

class ValidationError(SecurityError):
    """Ошибки валидации данных"""
    pass

class SecurityManager:
    """Централизованный менеджер безопасности"""
    
    def __init__(self):
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 минут
        self.failed_attempts = {}
        
    def hash_password(self, password: str) -> str:
        """
        Хеширование пароля с солью
        
        Args:
            password: Пароль для хеширования
            
        Returns:
            str: Хешированный пароль
        """
        if not password:
            raise ValidationError("Пароль не может быть пустым")
        
        # Генерируем соль
        salt = secrets.token_hex(16)
        
        # Создаем хеш
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Количество итераций
        )
        
        # Возвращаем соль + хеш
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Проверка пароля
        
        Args:
            password: Введенный пароль
            hashed_password: Хешированный пароль из БД
            
        Returns:
            bool: Результат проверки
        """
        if not password or not hashed_password:
            return False
        
        try:
            salt, stored_hash = hashed_password.split(':')
            
            # Вычисляем хеш для введенного пароля
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                salt.encode('utf-8'),
                100000
            )
            
            return secrets.compare_digest(stored_hash, password_hash.hex())
        except (ValueError, AttributeError):
            return False
    
    def verify_telegram_data(self, data: Dict[str, Any]) -> bool:
        """
        Верификация данных Telegram WebApp
        
        Args:
            data: Данные от Telegram
            
        Returns:
            bool: Результат верификации
        """
        if not data or not settings.telegram_bot_token:
            return False
        
        try:
            # Извлекаем hash из данных
            hash_value = data.pop('hash', None)
            if not hash_value:
                logger.warning("Отсутствует hash в данных Telegram")
                return False
            
            # Создаем строку для проверки
            check_string = '\n'.join([
                f"{key}={value}" for key, value in sorted(data.items())
            ])
            
            # Создаем секретный ключ
            secret_key = hashlib.sha256(settings.telegram_bot_token.encode()).digest()
            
            # Вычисляем ожидаемый hash
            expected_hash = hmac.new(
                secret_key,
                check_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Сравниваем хеши
            return secrets.compare_digest(hash_value, expected_hash)
        except Exception as e:
            logger.error(f"Ошибка верификации данных Telegram: {str(e)}")
            return False
    
    def sanitize_input(self, input_data: str, max_length: int = 1000) -> str:
        """
        Очистка входных данных от потенциально опасных символов
        
        Args:
            input_data: Входные данные
            max_length: Максимальная длина
            
        Returns:
            str: Очищенные данные
        """
        if not input_data:
            return ""
        
        # Ограничиваем длину
        if len(input_data) > max_length:
            input_data = input_data[:max_length]
        
        # Удаляем потенциально опасные символы
        cleaned = re.sub(r'[<>"\';\\]', '', input_data)
        
        return cleaned.strip()
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        Валидация номера телефона
        
        Args:
            phone: Номер телефона
            
        Returns:
            bool: Результат валидации
        """
        if not phone:
            return False
        
        # Убираем все нецифровые символы
        clean_phone = re.sub(r'\D', '', phone)
        
        # Проверяем длину (от 10 до 15 цифр)
        if len(clean_phone) < 10 or len(clean_phone) > 15:
            return False
        
        # Проверяем российские номера
        if clean_phone.startswith('7') and len(clean_phone) == 11:
            return True
        
        # Проверяем международные номера
        if len(clean_phone) >= 10:
            return True
        
        return False
    
    def validate_telegram_id(self, telegram_id: Any) -> bool:
        """
        Валидация Telegram ID
        
        Args:
            telegram_id: Telegram ID
            
        Returns:
            bool: Результат валидации
        """
        if not telegram_id:
            return False
        
        try:
            # Преобразуем в int
            tg_id = int(telegram_id)
            
            # Telegram ID должен быть положительным и не слишком большим
            return 1 <= tg_id <= 2**63 - 1
        except (ValueError, TypeError):
            return False
    
    def check_rate_limit(self, identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """
        Проверка лимита запросов
        
        Args:
            identifier: Идентификатор (IP, user_id и т.д.)
            max_requests: Максимальное количество запросов
            window_seconds: Временное окно в секундах
            
        Returns:
            bool: Разрешен ли запрос
        """
        current_time = time.time()
        
        # Инициализируем запись для идентификатора
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Очищаем старые записи
        self.failed_attempts[identifier] = [
            timestamp for timestamp in self.failed_attempts[identifier]
            if current_time - timestamp < window_seconds
        ]
        
        # Проверяем лимит
        if len(self.failed_attempts[identifier]) >= max_requests:
            return False
        
        # Добавляем текущий запрос
        self.failed_attempts[identifier].append(current_time)
        return True
    
    def validate_sql_input(self, input_data: Any) -> bool:
        """
        Проверка входных данных на SQL-инъекции
        
        Args:
            input_data: Входные данные
            
        Returns:
            bool: Безопасны ли данные
        """
        if not input_data:
            return True
        
        # Конвертируем в строку
        data_str = str(input_data).lower()
        
        # Список потенциально опасных SQL-ключевых слов
        dangerous_patterns = [
            'drop', 'delete', 'truncate', 'insert', 'update',
            'exec', 'execute', 'script', 'union', 'select',
            'create', 'alter', 'grant', 'revoke', '--', '/*',
            '*/', 'xp_', 'sp_'
        ]
        
        # Проверяем на наличие опасных паттернов
        for pattern in dangerous_patterns:
            if pattern in data_str:
                logger.warning(f"Обнаружен потенциально опасный паттерн: {pattern}")
                return False
        
        return True
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Генерация безопасного токена
        
        Args:
            length: Длина токена
            
        Returns:
            str: Безопасный токен
        """
        return secrets.token_urlsafe(length)
    
    def validate_file_upload(self, file_data: bytes, allowed_types: List[str], max_size: int = 10 * 1024 * 1024) -> bool:
        """
        Валидация загружаемых файлов
        
        Args:
            file_data: Данные файла
            allowed_types: Разрешенные типы файлов
            max_size: Максимальный размер файла
            
        Returns:
            bool: Разрешен ли файл
        """
        if not file_data:
            return False
        
        # Проверяем размер
        if len(file_data) > max_size:
            logger.warning(f"Файл слишком большой: {len(file_data)} байт")
            return False
        
        # Проверяем сигнатуру файла
        file_signatures = {
            'image/jpeg': [b'\xff\xd8\xff'],
            'image/png': [b'\x89PNG\r\n\x1a\n'],
            'image/gif': [b'GIF87a', b'GIF89a'],
            'application/pdf': [b'%PDF-']
        }
        
        for allowed_type in allowed_types:
            if allowed_type in file_signatures:
                for signature in file_signatures[allowed_type]:
                    if file_data.startswith(signature):
                        return True
        
        return False

# Глобальный экземпляр менеджера безопасности
security_manager = SecurityManager()

# Функции для обратной совместимости
def hash_password(password: str) -> str:
    """Хеширование пароля (обратная совместимость)"""
    return security_manager.hash_password(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Проверка пароля (обратная совместимость)"""
    return security_manager.verify_password(password, hashed_password)

def verify_telegram_data(data: Dict[str, Any]) -> bool:
    """Верификация данных Telegram (обратная совместимость)"""
    return security_manager.verify_telegram_data(data)

def sanitize_input(input_data: str, max_length: int = 1000) -> str:
    """Очистка входных данных (обратная совместимость)"""
    return security_manager.sanitize_input(input_data, max_length)

def validate_phone_number(phone: str) -> bool:
    """Валидация номера телефона (обратная совместимость)"""
    return security_manager.validate_phone_number(phone)

def validate_telegram_id(telegram_id: Any) -> bool:
    """Валидация Telegram ID (обратная совместимость)"""
    return security_manager.validate_telegram_id(telegram_id)

def check_rate_limit(identifier: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
    """Проверка лимита запросов (обратная совместимость)"""
    return security_manager.check_rate_limit(identifier, max_requests, window_seconds)

def validate_sql_input(input_data: Any) -> bool:
    """Проверка входных данных на SQL-инъекции (обратная совместимость)"""
    return security_manager.validate_sql_input(input_data)

def generate_secure_token(length: int = 32) -> str:
    """Генерация безопасного токена (обратная совместимость)"""
    return security_manager.generate_secure_token(length)

def validate_file_upload(file_data: bytes, allowed_types: List[str], max_size: int = 10 * 1024 * 1024) -> bool:
    """Валидация загружаемых файлов (обратная совместимость)"""
    return security_manager.validate_file_upload(file_data, allowed_types, max_size)
