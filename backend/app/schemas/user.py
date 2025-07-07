from pydantic import BaseModel, EmailStr, validator
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
    
    @validator('phone')
    def validate_phone(cls, v):
        # Убираем все нецифровые символы
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
    privacy_policy_accepted: bool = False
    driver_data: Optional[DriverData] = None
    
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
    driver_data: Optional[DriverData] = None
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None:
            phone_clean = re.sub(r'\D', '', v)
            if len(phone_clean) < 10:
                raise ValueError('Номер телефона должен содержать минимум 10 цифр')
            return phone_clean
        return v

class UserRead(UserBase):
    id: int
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
    rating: int
    total_rides: int
    cancelled_rides: int

    class Config:
        orm_mode = True

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