from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import re

class TelegramUserData(BaseModel):
    """Схема для валидации данных пользователя Telegram"""
    id: int = Field(..., gt=0, description="Telegram ID пользователя")
    first_name: str = Field(..., min_length=1, max_length=64, description="Имя пользователя")
    last_name: Optional[str] = Field(None, max_length=64, description="Фамилия пользователя")
    username: Optional[str] = Field(None, max_length=32, description="Username пользователя")
    photo_url: Optional[str] = Field(None, max_length=500, description="URL фото профиля")
    auth_date: int = Field(..., gt=0, description="Дата авторизации")
    hash: Optional[str] = Field(None, max_length=128, description="Подпись данных")
    
    @validator('username')
    def validate_username(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9_]{5,32}$', v):
                raise ValueError('Username должен содержать только буквы, цифры и подчеркивания (5-32 символа)')
        return v
    
    @validator('photo_url')
    def validate_photo_url(cls, v):
        if v is not None:
            if not v.startswith(('http://', 'https://')):
                raise ValueError('URL фото должен начинаться с http:// или https://')
        return v

class TelegramWebAppData(BaseModel):
    """Схема для валидации данных Telegram Web App"""
    user: TelegramUserData = Field(..., description="Данные пользователя")
    query_id: Optional[str] = Field(None, max_length=64, description="ID запроса")
    hash: Optional[str] = Field(None, max_length=128, description="Подпись данных")
    
    class Config:
        extra = "allow"  # Разрешаем дополнительные поля для совместимости

class TelegramVerificationRequest(BaseModel):
    """Схема для запроса верификации Telegram"""
    telegram_data: TelegramWebAppData = Field(..., description="Данные от Telegram Web App")
    
    @validator('telegram_data')
    def validate_telegram_data(cls, v):
        # Дополнительная валидация даты авторизации
        current_time = int(datetime.now().timestamp())
        if v.user.auth_date > current_time:
            raise ValueError('Дата авторизации не может быть в будущем')
        
        # Проверяем, что данные не старше 24 часов
        if current_time - v.user.auth_date > 86400:
            raise ValueError('Данные авторизации устарели (старше 24 часов)')
        
        return v

class TelegramAuthRequest(BaseModel):
    """Схема для совместимости с фронтендом"""
    user: TelegramUserData = Field(..., description="Данные пользователя")
    auth_date: Optional[int] = Field(None, description="Дата авторизации")
    hash: Optional[str] = Field(None, max_length=128, description="Подпись данных")
    initData: Optional[str] = Field(None, description="Инициализационные данные")
    query_id: Optional[str] = Field(None, max_length=64, description="ID запроса")
    start_param: Optional[str] = Field(None, max_length=64, description="Параметр запуска")
    
    class Config:
        extra = "allow"  # Разрешаем дополнительные поля для совместимости
    
    @validator('auth_date')
    def validate_auth_date(cls, v):
        if v is not None:
            current_time = int(datetime.now().timestamp())
            if v > current_time:
                raise ValueError('Дата авторизации не может быть в будущем')
            
            # Проверяем, что данные не старше 24 часов
            if current_time - v > 86400:
                raise ValueError('Данные авторизации устарели (старше 24 часов)')
        return v 