from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, JSON, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    name = Column(String)  # Для совместимости с фронтендом
    birth_date = Column(Date, nullable=False)
    city = Column(String, nullable=False)
    avatar_url = Column(String)
    avatar = Column(String)  # Для совместимости с фронтендом
    
    # Статус и верификация
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    is_driver = Column(Boolean, default=False, index=True)
    verified = Column(JSON, default=dict)  # Для совместимости с фронтендом
    
    # Соглашения
    privacy_policy_version = Column(String, default="1.1")
    privacy_policy_accepted = Column(Boolean, default=False)
    privacy_policy_accepted_at = Column(DateTime)
    
    # Водительские данные (опциональные)
    car_brand = Column(String)
    car_model = Column(String)
    car_year = Column(Integer)
    car_color = Column(String)
    driver_license_number = Column(String)
    driver_license_photo_url = Column(String)
    car_photo_url = Column(String)
    car = Column(JSON, default=dict)  # Для совместимости с фронтендом
    
    # Метаданные
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Дополнительные поля
    average_rating = Column(Float, default=0.0, index=True)
    rating = Column(Integer, default=0)  # Для совместимости с фронтендом
    balance = Column(Integer, default=500, index=True)  # Баланс пользователя
    reviews = Column(Integer, default=0)  # Количество отзывов
    total_rides = Column(Integer, default=0)
    cancelled_rides = Column(Integer, default=0, index=True)
    
    # История изменений (JSON)
    profile_history = Column(JSON, default=list)

    # Отношения для рейтингов и отзывов
    ratings_given = relationship("Rating", foreign_keys="Rating.from_user_id", back_populates="from_user")
    ratings_received = relationship("Rating", foreign_keys="Rating.target_user_id", back_populates="target_user")
    reviews_given = relationship("Review", foreign_keys="Review.from_user_id", back_populates="from_user")
    reviews_received = relationship("Review", foreign_keys="Review.target_user_id", back_populates="target_user")
    
    # Отношения для платежей
    payments = relationship("Payment", back_populates="user")
    
    # Индексы для улучшения производительности
    __table_args__ = (
        Index('idx_user_telegram_phone', 'telegram_id', 'phone'),
        Index('idx_user_status', 'is_active', 'is_verified', 'is_driver'),
        Index('idx_user_rating_balance', 'average_rating', 'balance'),
        Index('idx_user_created', 'created_at'),
        Index('idx_user_city', 'city'),  # Для поиска по городу
        Index('idx_user_birth_date', 'birth_date'),  # Для возрастных ограничений
        Index('idx_user_driver_license', 'driver_license_number'),  # Для проверки водительских прав
        Index('idx_user_car_info', 'car_brand', 'car_model'),  # Для поиска по автомобилю
        Index('idx_user_updated', 'updated_at'),  # Для отслеживания изменений
        Index('idx_user_rating_reviews', 'average_rating', 'reviews'),  # Для рейтингов
    )

class ProfileChangeLog(Base):
    __tablename__ = 'profile_change_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    field_name = Column(String, nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_at = Column(DateTime, default=func.now(), index=True)
    changed_by = Column(String, default="user")  # user, admin, system
    
    # Индексы для улучшения производительности
    __table_args__ = (
        Index('idx_profile_log_user_date', 'user_id', 'changed_at'),
        Index('idx_profile_log_field', 'field_name'),
    ) 