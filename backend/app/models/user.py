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
    

    
    # Оптимизированные индексы для улучшения производительности
    __table_args__ = (
        # Основные индексы для поиска
        Index('idx_user_telegram_active', 'telegram_id', 'is_active'),
        Index('idx_user_phone_active', 'phone', 'is_active'),
        Index('idx_user_city_active', 'city', 'is_active'),
        
        # Индексы для водителей
        Index('idx_user_driver_status', 'is_driver', 'is_active', 'is_verified'),
        Index('idx_user_driver_city', 'city', 'is_driver', 'is_active'),
        
        # Индексы для рейтингов
        Index('idx_user_rating', 'average_rating', 'is_active'),
        Index('idx_user_rating_city', 'city', 'average_rating', 'is_active'),
        
        # Временные индексы
        Index('idx_user_created_active', 'created_at', 'is_active'),
        Index('idx_user_updated', 'updated_at'),
        
        # Индексы для статистики
        Index('idx_user_rides_stats', 'total_rides', 'cancelled_rides', 'is_active'),
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