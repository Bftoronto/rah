from pydantic import BaseModel, EmailStr, validator, root_validator
from typing import Optional, List
from datetime import datetime, date
import re

class UserBase(BaseModel):
    id: Optional[int] = None
    telegram_id: str
    phone: str
    full_name: str
    birth_date: date
    city: str
    avatar_url: Optional[str] = None
    
    # Основные поля для совместимости с фронтендом
    name: Optional[str] = None
    balance: int = 500
    reviews: int = 0
    avatar: Optional[str] = None
    verified: dict = {}
    car: dict = {}
    average_rating: float = 0.0
    rating: int = 0
    total_rides: int = 0
    cancelled_rides: int = 0
    profile_history: Optional[list] = []
    is_active: bool = True
    is_verified: bool = False
    is_driver: bool = False
    privacy_policy_version: str = "1.1"
    privacy_policy_accepted: bool = False
    privacy_policy_accepted_at: Optional[datetime] = None
    
    # Водительские данные
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    car_year: Optional[int] = None
    car_color: Optional[str] = None
    driver_license_number: Optional[str] = None
    driver_license_photo_url: Optional[str] = None
    car_photo_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        phone_clean = re.sub(r'\D', '', v)
        if len(phone_clean) < 10:
            raise ValueError('Номер телефона должен содержать минимум 10 цифр')
        return phone_clean
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('ФИО должно содержать минимум 2 символа')
        return v.strip()
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('Пользователь должен быть старше 18 лет')
        if age > 100:
            raise ValueError('Некорректная дата рождения')
        return v

class UserRead(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_driver: bool
    privacy_policy_version: str
    privacy_policy_accepted: bool
    privacy_policy_accepted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    
    @root_validator(pre=False)
    def set_compatibility_fields(cls, values):
        """Устанавливаем поля для совместимости с фронтендом"""
        # Синхронизируем name с full_name
        if 'full_name' in values and not values.get('name'):
            values['name'] = values['full_name']
        
        # Синхронизируем avatar с avatar_url
        if 'avatar_url' in values and not values.get('avatar'):
            values['avatar'] = values['avatar_url']
        
        # Синхронизируем rating с average_rating
        if 'average_rating' in values and not values.get('rating'):
            values['rating'] = int(values['average_rating'])
        
        # Устанавливаем verified статус
        if not values.get('verified'):
            values['verified'] = {
                'phone': bool(values.get('phone')),
                'email': False,
                'identity': values.get('is_verified', False)
            }
        
        # Устанавливаем информацию об автомобиле
        if not values.get('car'):
            values['car'] = {
                'brand': values.get('car_brand'),
                'model': values.get('car_model'), 
                'year': values.get('car_year'),
                'color': values.get('car_color'),
                'photo_url': values.get('car_photo_url')
            }
        
        return values

class UserCreate(UserBase):
    driver_data: Optional['DriverData'] = None
    
    @validator('privacy_policy_accepted')
    def validate_privacy_policy(cls, v):
        if not v:
            raise ValueError('Необходимо принять пользовательское соглашение')
        return v

class UserUpdate(BaseModel):
    phone: Optional[str] = None
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    city: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Поля совместимости
    name: Optional[str] = None
    avatar: Optional[str] = None
    balance: Optional[int] = None
    reviews: Optional[int] = None
    rating: Optional[int] = None
    verified: Optional[dict] = None
    car: Optional[dict] = None
    
    # Водительские данные
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    car_year: Optional[int] = None
    car_color: Optional[str] = None
    driver_license_number: Optional[str] = None
    driver_license_photo_url: Optional[str] = None
    car_photo_url: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            phone_clean = re.sub(r'\D', '', v)
            if len(phone_clean) < 10:
                raise ValueError('Номер телефона должен содержать минимум 10 цифр')
            return phone_clean
        return v
    
    @root_validator(pre=False)
    def sync_fields(cls, values):
        """Синхронизируем поля для обратной совместимости"""
        # name -> full_name
        if values.get('name') and not values.get('full_name'):
            values['full_name'] = values['name']
        
        # avatar -> avatar_url
        if values.get('avatar') and not values.get('avatar_url'):
            values['avatar_url'] = values['avatar']
        
        # Извлекаем данные автомобиля из car объекта
        if values.get('car'):
            car_data = values['car']
            if isinstance(car_data, dict):
                if car_data.get('brand') and not values.get('car_brand'):
                    values['car_brand'] = car_data['brand']
                if car_data.get('model') and not values.get('car_model'):
                    values['car_model'] = car_data['model']
                if car_data.get('year') and not values.get('car_year'):
                    values['car_year'] = car_data['year']
                if car_data.get('color') and not values.get('car_color'):
                    values['car_color'] = car_data['color']
                if car_data.get('photo_url') and not values.get('car_photo_url'):
                    values['car_photo_url'] = car_data['photo_url']
        
        return values

class DriverData(BaseModel):
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    car_year: Optional[int] = None
    car_color: Optional[str] = None
    driver_license_number: Optional[str] = None
    driver_license_photo_url: Optional[str] = None
    car_photo_url: Optional[str] = None
    
    @validator('car_year')
    def validate_car_year(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1900 or v > current_year + 1:
                raise ValueError('Некорректный год выпуска автомобиля')
        return v

class PrivacyPolicyAccept(BaseModel):
    accepted: bool
    version: str = "1.1"

class ProfileHistoryEntry(BaseModel):
    field_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    changed_at: datetime
    changed_by: str

class ProfileHistory(BaseModel):
    user_id: int
    entries: List[ProfileHistoryEntry]

# Для обратной совместимости
UserRead.update_forward_refs()
UserCreate.update_forward_refs()
