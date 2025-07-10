"""
Система локализации для ошибок и сообщений
Поддерживает русский и английский языки
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class LocalizationManager:
    """Менеджер локализации для управления переводами"""
    
    def __init__(self):
        self.translations = {}
        self.default_language = "ru"
        self.supported_languages = ["ru", "en"]
        self.load_translations()
    
    def load_translations(self):
        """Загрузка переводов из файлов"""
        translations_dir = Path(__file__).parent.parent / "locales"
        
        # Создаем директорию если не существует
        translations_dir.mkdir(exist_ok=True)
        
        for lang in self.supported_languages:
            lang_file = translations_dir / f"{lang}.json"
            
            if lang_file.exists():
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
            else:
                # Создаем файл с базовыми переводами
                self.translations[lang] = self.get_default_translations(lang)
                self.save_translations(lang)
    
    def save_translations(self, language: str):
        """Сохранение переводов в файл"""
        translations_dir = Path(__file__).parent.parent / "locales"
        lang_file = translations_dir / f"{language}.json"
        
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(self.translations[language], f, ensure_ascii=False, indent=2)
    
    def get_default_translations(self, language: str) -> Dict[str, Any]:
        """Получение базовых переводов для языка"""
        if language == "ru":
            return {
                "errors": {
                    "validation": {
                        "title": "Ошибка валидации",
                        "invalid_data": "Некорректные данные",
                        "required_field": "Обязательное поле",
                        "invalid_format": "Неверный формат",
                        "too_short": "Слишком короткое значение",
                        "too_long": "Слишком длинное значение",
                        "invalid_email": "Неверный формат email",
                        "invalid_phone": "Неверный формат телефона",
                        "invalid_date": "Неверный формат даты",
                        "invalid_rating": "Рейтинг должен быть от 1 до 5",
                        "invalid_price": "Неверная цена",
                        "invalid_seats": "Неверное количество мест"
                    },
                    "authentication": {
                        "title": "Ошибка аутентификации",
                        "invalid_credentials": "Неверные учетные данные",
                        "token_expired": "Токен истек",
                        "token_invalid": "Недействительный токен",
                        "user_not_found": "Пользователь не найден",
                        "unauthorized": "Не авторизован",
                        "forbidden": "Доступ запрещен",
                        "telegram_verification_failed": "Ошибка верификации Telegram"
                    },
                    "authorization": {
                        "title": "Ошибка авторизации",
                        "insufficient_permissions": "Недостаточно прав",
                        "driver_required": "Требуются права водителя",
                        "verified_user_required": "Требуется верифицированный пользователь"
                    },
                    "not_found": {
                        "title": "Не найдено",
                        "user_not_found": "Пользователь не найден",
                        "ride_not_found": "Поездка не найдена",
                        "rating_not_found": "Рейтинг не найден",
                        "message_not_found": "Сообщение не найдено",
                        "file_not_found": "Файл не найден"
                    },
                    "server": {
                        "title": "Ошибка сервера",
                        "internal_error": "Внутренняя ошибка сервера",
                        "database_error": "Ошибка базы данных",
                        "file_upload_error": "Ошибка загрузки файла",
                        "external_service_error": "Ошибка внешнего сервиса"
                    },
                    "rate_limit": {
                        "title": "Превышен лимит запросов",
                        "too_many_requests": "Слишком много запросов",
                        "try_later": "Попробуйте позже"
                    },
                    "business_logic": {
                        "title": "Ошибка бизнес-логики",
                        "ride_already_booked": "Поездка уже забронирована",
                        "insufficient_seats": "Недостаточно мест",
                        "ride_in_past": "Поездка в прошлом",
                        "self_rating": "Нельзя оценить самого себя",
                        "duplicate_rating": "Рейтинг уже существует"
                    }
                },
                "success": {
                    "user_registered": "Пользователь успешно зарегистрирован",
                    "user_updated": "Пользователь успешно обновлен",
                    "ride_created": "Поездка успешно создана",
                    "ride_updated": "Поездка успешно обновлена",
                    "ride_deleted": "Поездка успешно удалена",
                    "rating_created": "Рейтинг успешно создан",
                    "rating_updated": "Рейтинг успешно обновлен",
                    "message_sent": "Сообщение успешно отправлено",
                    "file_uploaded": "Файл успешно загружен",
                    "settings_updated": "Настройки успешно обновлены"
                },
                "messages": {
                    "welcome": "Добро пожаловать в PAX!",
                    "ride_search_results": "Найдено {count} поездок",
                    "no_rides_found": "Поездки не найдены",
                    "booking_confirmed": "Бронирование подтверждено",
                    "payment_successful": "Оплата прошла успешно",
                    "notification_sent": "Уведомление отправлено"
                }
            }
        elif language == "en":
            return {
                "errors": {
                    "validation": {
                        "title": "Validation Error",
                        "invalid_data": "Invalid data",
                        "required_field": "Required field",
                        "invalid_format": "Invalid format",
                        "too_short": "Value too short",
                        "too_long": "Value too long",
                        "invalid_email": "Invalid email format",
                        "invalid_phone": "Invalid phone format",
                        "invalid_date": "Invalid date format",
                        "invalid_rating": "Rating must be between 1 and 5",
                        "invalid_price": "Invalid price",
                        "invalid_seats": "Invalid number of seats"
                    },
                    "authentication": {
                        "title": "Authentication Error",
                        "invalid_credentials": "Invalid credentials",
                        "token_expired": "Token expired",
                        "token_invalid": "Invalid token",
                        "user_not_found": "User not found",
                        "unauthorized": "Unauthorized",
                        "forbidden": "Forbidden",
                        "telegram_verification_failed": "Telegram verification failed"
                    },
                    "authorization": {
                        "title": "Authorization Error",
                        "insufficient_permissions": "Insufficient permissions",
                        "driver_required": "Driver permissions required",
                        "verified_user_required": "Verified user required"
                    },
                    "not_found": {
                        "title": "Not Found",
                        "user_not_found": "User not found",
                        "ride_not_found": "Ride not found",
                        "rating_not_found": "Rating not found",
                        "message_not_found": "Message not found",
                        "file_not_found": "File not found"
                    },
                    "server": {
                        "title": "Server Error",
                        "internal_error": "Internal server error",
                        "database_error": "Database error",
                        "file_upload_error": "File upload error",
                        "external_service_error": "External service error"
                    },
                    "rate_limit": {
                        "title": "Rate Limit Exceeded",
                        "too_many_requests": "Too many requests",
                        "try_later": "Try again later"
                    },
                    "business_logic": {
                        "title": "Business Logic Error",
                        "ride_already_booked": "Ride already booked",
                        "insufficient_seats": "Insufficient seats",
                        "ride_in_past": "Ride in the past",
                        "self_rating": "Cannot rate yourself",
                        "duplicate_rating": "Rating already exists"
                    }
                },
                "success": {
                    "user_registered": "User successfully registered",
                    "user_updated": "User successfully updated",
                    "ride_created": "Ride successfully created",
                    "ride_updated": "Ride successfully updated",
                    "ride_deleted": "Ride successfully deleted",
                    "rating_created": "Rating successfully created",
                    "rating_updated": "Rating successfully updated",
                    "message_sent": "Message successfully sent",
                    "file_uploaded": "File successfully uploaded",
                    "settings_updated": "Settings successfully updated"
                },
                "messages": {
                    "welcome": "Welcome to PAX!",
                    "ride_search_results": "Found {count} rides",
                    "no_rides_found": "No rides found",
                    "booking_confirmed": "Booking confirmed",
                    "payment_successful": "Payment successful",
                    "notification_sent": "Notification sent"
                }
            }
        else:
            return {}
    
    def get_message(self, key: str, language: str = None, **kwargs) -> str:
        """Получение переведенного сообщения"""
        if language is None:
            language = self.default_language
        
        if language not in self.supported_languages:
            language = self.default_language
        
        # Разбираем ключ по точкам (например: "errors.validation.title")
        keys = key.split('.')
        current = self.translations.get(language, {})
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                # Возвращаем ключ если перевод не найден
                return key
        
        # Если это строка, форматируем её с параметрами
        if isinstance(current, str):
            try:
                return current.format(**kwargs)
            except (KeyError, ValueError):
                return current
        
        return str(current)
    
    def get_error_message(self, error_code: str, language: str = None, **kwargs) -> str:
        """Получение сообщения об ошибке"""
        return self.get_message(f"errors.{error_code}", language, **kwargs)
    
    def get_success_message(self, success_code: str, language: str = None, **kwargs) -> str:
        """Получение сообщения об успехе"""
        return self.get_message(f"success.{success_code}", language, **kwargs)
    
    def get_general_message(self, message_code: str, language: str = None, **kwargs) -> str:
        """Получение общего сообщения"""
        return self.get_message(f"messages.{message_code}", language, **kwargs)
    
    def add_translation(self, language: str, key: str, value: str):
        """Добавление нового перевода"""
        if language not in self.translations:
            self.translations[language] = {}
        
        keys = key.split('.')
        current = self.translations[language]
        
        # Создаем вложенные словари
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Устанавливаем значение
        current[keys[-1]] = value
        
        # Сохраняем в файл
        self.save_translations(language)
    
    def get_supported_languages(self) -> list:
        """Получение списка поддерживаемых языков"""
        return self.supported_languages.copy()
    
    def set_default_language(self, language: str):
        """Установка языка по умолчанию"""
        if language in self.supported_languages:
            self.default_language = language

# Глобальный экземпляр менеджера локализации
localization_manager = LocalizationManager()

# Утилитарные функции для удобного использования
def get_message(key: str, language: str = None, **kwargs) -> str:
    """Получение переведенного сообщения"""
    return localization_manager.get_message(key, language, **kwargs)

def get_error_message(error_code: str, language: str = None, **kwargs) -> str:
    """Получение сообщения об ошибке"""
    return localization_manager.get_error_message(error_code, language, **kwargs)

def get_success_message(success_code: str, language: str = None, **kwargs) -> str:
    """Получение сообщения об успехе"""
    return localization_manager.get_success_message(success_code, language, **kwargs)

def get_general_message(message_code: str, language: str = None, **kwargs) -> str:
    """Получение общего сообщения"""
    return localization_manager.get_general_message(message_code, language, **kwargs)

def add_translation(language: str, key: str, value: str):
    """Добавление нового перевода"""
    localization_manager.add_translation(language, key, value)

def get_supported_languages() -> list:
    """Получение списка поддерживаемых языков"""
    return localization_manager.get_supported_languages()

def set_default_language(language: str):
    """Установка языка по умолчанию"""
    localization_manager.set_default_language(language) 