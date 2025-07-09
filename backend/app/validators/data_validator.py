import re
from datetime import datetime, date
from typing import Dict, Any, Optional
from ..schemas.user import UserCreate, UserUpdate
from ..interfaces.auth import IValidator
from ..utils.logger import get_logger, security_logger

logger = get_logger("data_validator")

class DataValidator(IValidator):
    """Валидатор данных с централизованной логикой проверки"""
    
    def __init__(self):
        # Регулярные выражения для валидации
        self.phone_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.username_pattern = re.compile(r'^[a-zA-Z0-9_]{3,32}$')
        self.url_pattern = re.compile(r'^https?://.+')
    
    def validate_telegram_data(self, data: Dict[str, Any]) -> bool:
        """Валидация данных Telegram"""
        try:
            # Проверяем обязательные поля
            required_fields = ['id', 'first_name', 'auth_date']
            for field in required_fields:
                if field not in data:
                    security_logger.data_validation_error(field, None, "required")
                    return False
            
            # Проверяем тип ID
            try:
                telegram_id = int(data['id'])
                if telegram_id <= 0:
                    security_logger.data_validation_error("id", data['id'], "invalid_format")
                    return False
            except (ValueError, TypeError):
                security_logger.data_validation_error("id", data['id'], "invalid_type")
                return False
            
            # Проверяем имя
            if not data['first_name'] or len(data['first_name'].strip()) < 1:
                security_logger.data_validation_error("first_name", data['first_name'], "empty")
                return False
            
            # Проверяем дату авторизации
            try:
                auth_date = int(data['auth_date'])
                current_time = int(datetime.now().timestamp())
                if auth_date > current_time:
                    security_logger.data_validation_error("auth_date", data['auth_date'], "future_date")
                    return False
                if current_time - auth_date > 86400:  # 24 часа
                    security_logger.data_validation_error("auth_date", data['auth_date'], "expired")
                    return False
            except (ValueError, TypeError):
                security_logger.data_validation_error("auth_date", data['auth_date'], "invalid_format")
                return False
            
            # Проверяем username если есть
            if 'username' in data and data['username']:
                if not self.username_pattern.match(data['username']):
                    security_logger.data_validation_error("username", data['username'], "invalid_format")
                    return False
            
            # Проверяем URL фото если есть
            if 'photo_url' in data and data['photo_url']:
                if not self.url_pattern.match(data['photo_url']):
                    security_logger.data_validation_error("photo_url", data['photo_url'], "invalid_url")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации данных Telegram: {str(e)}")
            return False
    
    def validate_user_data(self, user_data: UserCreate) -> bool:
        """Валидация данных пользователя при создании"""
        try:
            # Проверяем Telegram ID
            if not user_data.telegram_id:
                security_logger.data_validation_error("telegram_id", None, "required")
                return False
            
            # Проверяем имя
            if not user_data.full_name or len(user_data.full_name.strip()) < 2:
                security_logger.data_validation_error("full_name", user_data.full_name, "too_short")
                return False
            
            # Проверяем телефон если есть
            if user_data.phone:
                if not self.phone_pattern.match(user_data.phone):
                    security_logger.data_validation_error("phone", user_data.phone, "invalid_format")
                    return False
            
            # Проверяем дату рождения если есть
            if user_data.birth_date:
                if user_data.birth_date > date.today():
                    security_logger.data_validation_error("birth_date", str(user_data.birth_date), "future_date")
                    return False
                
                # Проверяем, что пользователю не менее 18 лет
                age = (date.today() - user_data.birth_date).days // 365
                if age < 18:
                    security_logger.data_validation_error("birth_date", str(user_data.birth_date), "underage")
                    return False
            
            # Проверяем город если есть
            if user_data.city and len(user_data.city.strip()) < 2:
                security_logger.data_validation_error("city", user_data.city, "too_short")
                return False
            
            # Проверяем URL аватара если есть
            if user_data.avatar_url and not self.url_pattern.match(user_data.avatar_url):
                security_logger.data_validation_error("avatar_url", user_data.avatar_url, "invalid_url")
                return False
            
            # Проверяем водительские данные если пользователь водитель
            if user_data.is_driver:
                if not self._validate_driver_data(user_data):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации данных пользователя: {str(e)}")
            return False
    
    def validate_user_update(self, user_data: UserUpdate) -> bool:
        """Валидация данных пользователя при обновлении"""
        try:
            # Проверяем имя если обновляется
            if user_data.full_name is not None:
                if len(user_data.full_name.strip()) < 2:
                    security_logger.data_validation_error("full_name", user_data.full_name, "too_short")
                    return False
            
            # Проверяем телефон если обновляется
            if user_data.phone is not None:
                if user_data.phone and not self.phone_pattern.match(user_data.phone):
                    security_logger.data_validation_error("phone", user_data.phone, "invalid_format")
                    return False
            
            # Проверяем дату рождения если обновляется
            if user_data.birth_date is not None:
                if user_data.birth_date > date.today():
                    security_logger.data_validation_error("birth_date", str(user_data.birth_date), "future_date")
                    return False
                
                # Проверяем, что пользователю не менее 18 лет
                age = (date.today() - user_data.birth_date).days // 365
                if age < 18:
                    security_logger.data_validation_error("birth_date", str(user_data.birth_date), "underage")
                    return False
            
            # Проверяем город если обновляется
            if user_data.city is not None:
                if user_data.city and len(user_data.city.strip()) < 2:
                    security_logger.data_validation_error("city", user_data.city, "too_short")
                    return False
            
            # Проверяем URL аватара если обновляется
            if user_data.avatar_url is not None:
                if user_data.avatar_url and not self.url_pattern.match(user_data.avatar_url):
                    security_logger.data_validation_error("avatar_url", user_data.avatar_url, "invalid_url")
                    return False
            
            # Проверяем водительские данные если обновляются
            if user_data.driver_data:
                if not self._validate_driver_update_data(user_data.driver_data):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации обновления пользователя: {str(e)}")
            return False
    
    def _validate_driver_data(self, user_data: UserCreate) -> bool:
        """Валидация водительских данных"""
        try:
            # Проверяем номер водительских прав
            if user_data.driver_license_number:
                if len(user_data.driver_license_number) < 10:
                    security_logger.data_validation_error("driver_license_number", user_data.driver_license_number, "too_short")
                    return False
            
            # Проверяем год автомобиля
            if user_data.car_year:
                current_year = datetime.now().year
                if user_data.car_year < 1900 or user_data.car_year > current_year + 1:
                    security_logger.data_validation_error("car_year", user_data.car_year, "invalid_year")
                    return False
            
            # Проверяем URL фото прав
            if user_data.driver_license_photo_url and not self.url_pattern.match(user_data.driver_license_photo_url):
                security_logger.data_validation_error("driver_license_photo_url", user_data.driver_license_photo_url, "invalid_url")
                return False
            
            # Проверяем URL фото автомобиля
            if user_data.car_photo_url and not self.url_pattern.match(user_data.car_photo_url):
                security_logger.data_validation_error("car_photo_url", user_data.car_photo_url, "invalid_url")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации водительских данных: {str(e)}")
            return False
    
    def _validate_driver_update_data(self, driver_data) -> bool:
        """Валидация обновления водительских данных"""
        try:
            # Проверяем номер водительских прав
            if driver_data.driver_license_number:
                if len(driver_data.driver_license_number) < 10:
                    security_logger.data_validation_error("driver_license_number", driver_data.driver_license_number, "too_short")
                    return False
            
            # Проверяем год автомобиля
            if driver_data.car_year:
                current_year = datetime.now().year
                if driver_data.car_year < 1900 or driver_data.car_year > current_year + 1:
                    security_logger.data_validation_error("car_year", driver_data.car_year, "invalid_year")
                    return False
            
            # Проверяем URL фото прав
            if driver_data.driver_license_photo_url and not self.url_pattern.match(driver_data.driver_license_photo_url):
                security_logger.data_validation_error("driver_license_photo_url", driver_data.driver_license_photo_url, "invalid_url")
                return False
            
            # Проверяем URL фото автомобиля
            if driver_data.car_photo_url and not self.url_pattern.match(driver_data.car_photo_url):
                security_logger.data_validation_error("car_photo_url", driver_data.car_photo_url, "invalid_url")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации обновления водительских данных: {str(e)}")
            return False
    
    def validate_ride_data(self, ride_data) -> bool:
        """Валидация данных поездки"""
        try:
            # Проверяем места отправления и назначения
            if not ride_data.from_location or len(ride_data.from_location.strip()) < 2:
                return False
            
            if not ride_data.to_location or len(ride_data.to_location.strip()) < 2:
                return False
            
            # Проверяем количество мест
            if ride_data.seats <= 0 or ride_data.seats > 8:
                return False
            
            # Проверяем цену
            if ride_data.price <= 0:
                return False
            
            # Проверяем дату
            if ride_data.date <= datetime.now():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка валидации данных поездки: {str(e)}")
            return False 