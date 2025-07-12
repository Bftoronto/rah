from pydantic import BaseModel, EmailStr, validator, Field, root_validator
from typing import Optional, List
from datetime import datetime, date
import re

class UserBase(BaseModel):
    telegram_id: str
    phone: str
    full_name: str
    birth_date: date
    city: str
    avatar_url: Optional[str] = None
    
    # Основные поля для совместимости с фронтендом
    is_active: bool = True
    is_verified: bool = False
    is_driver: bool = False
    privacy_policy_version: str = "1.1"
    privacy_policy_accepted: bool = False
    
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
        if not v:
            raise ValueError('Номер телефона обязателен')
        phone_clean = re.sub(r'\D', '', v)
        if len(phone_clean) < 10:
            raise ValueError('Номер телефона должен содержать минимум 10 цифр')
        return phone_clean

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('ФИО должно содержать минимум 2 символа')
        return v.strip()

    @validator('birth_date')
    def validate_birth_date(cls, v):
        if not v:
            raise ValueError('Дата рождения обязательна')
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('Пользователь должен быть старше 18 лет')
        if age > 100:
            raise ValueError('Некорректная дата рождения')
        return v

    @validator('city')
    def validate_city(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Город должен содержать минимум 2 символа')
        return v.strip()

    @validator('telegram_id')
    def validate_telegram_id(cls, v):
        if not v:
            raise ValueError('Telegram ID обязателен')
        return str(v)

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

class UserCreate(UserBase):
    """
    Схема создания пользователя. Использует строгую валидацию UserBase и расширяет только необходимыми полями.
    """
    privacy_policy_accepted: bool = Field(..., description="Принятие пользовательского соглашения")
    
    @validator('privacy_policy_accepted')
    def validate_privacy_policy(cls, v):
        if not v:
            raise ValueError('Необходимо принять пользовательское соглашение')
        return v

class UserUpdate(BaseModel):
    """
    Схема обновления пользователя. Все поля опциональны с валидацией.
    """
    phone: Optional[str] = None
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    city: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_driver: Optional[bool] = None
    privacy_policy_version: Optional[str] = None
    privacy_policy_accepted: Optional[bool] = None
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    car_year: Optional[int] = None
    car_color: Optional[str] = None
    driver_license_number: Optional[str] = None
    driver_license_photo_url: Optional[str] = None
    car_photo_url: Optional[str] = None
    driver_data: Optional[DriverData] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            phone_clean = re.sub(r'\D', '', v)
            if len(phone_clean) < 10:
                raise ValueError('Номер телефона должен содержать минимум 10 цифр')
            return phone_clean
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('ФИО должно содержать минимум 2 символа')
        return v.strip() if v else v
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        if v is not None:
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 18:
                raise ValueError('Пользователь должен быть старше 18 лет')
            if age > 100:
                raise ValueError('Некорректная дата рождения')
        return v
    
    @validator('city')
    def validate_city(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError('Город должен содержать минимум 2 символа')
        return v.strip() if v else v

class UserRead(UserBase):
    id: int
    # Прямые поля для совместимости с фронтендом
    name: Optional[str] = None  # Прямое поле вместо алиаса
    balance: int = 500  # Для совместимости с фронтендом
    reviews: int = 0  # Для совместимости с фронтендом
    avatar: Optional[str] = None  # Прямое поле вместо алиаса
    verified: dict = {}  # Для совместимости с фронтендом
    car: dict = {}  # Для совместимости с фронтендом
    is_active: bool
    is_verified: bool
    is_driver: bool
    privacy_policy_version: str
    privacy_policy_accepted: bool
    privacy_policy_accepted_at: Optional[datetime]
    car_brand: Optional[str]
    car_model: Optional[str]
    car_year: Optional[int]
    car_color: Optional[str]
    driver_license_number: Optional[str]
    driver_license_photo_url: Optional[str]
    car_photo_url: Optional[str]
    created_at: datetime
    updated_at: datetime
    average_rating: float = 0.0
    rating: int = 0  # Прямое поле для совместимости
    total_rides: int
    cancelled_rides: int
    profile_history: Optional[list] = []

    @root_validator(pre=True)
    def set_compatibility_fields(cls, values):
        """Устанавливает поля для совместимости с фронтендом"""
        # Копируем full_name в name
        if 'full_name' in values and values['full_name']:
            values['name'] = values['full_name']
        
        # Копируем avatar_url в avatar
        if 'avatar_url' in values and values['avatar_url']:
            values['avatar'] = values['avatar_url']
        
        # Устанавливаем verified на основе is_verified
        if 'is_verified' in values:
            values['verified'] = {
                'status': values['is_verified'],
                'verified_at': values.get('created_at')
            }
        
        # Устанавливаем car на основе данных автомобиля
        car_data = {}
        if values.get('car_brand'):
            car_data['brand'] = values['car_brand']
        if values.get('car_model'):
            car_data['model'] = values['car_model']
        if values.get('car_year'):
            car_data['year'] = values['car_year']
        if values.get('car_color'):
            car_data['color'] = values['car_color']
        if values.get('car_photo_url'):
            car_data['photo'] = values['car_photo_url']
        
        values['car'] = car_data
        
        # Устанавливаем rating на основе average_rating
        if 'average_rating' in values:
            values['rating'] = int(values['average_rating'])
        
        return values

    class Config:
        from_attributes = True
        populate_by_name = True
        validate_by_name = True

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