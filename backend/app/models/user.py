from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Date, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    
    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    city = Column(String, nullable=False)
    avatar_url = Column(String)
    
    # Статус и верификация
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_driver = Column(Boolean, default=False)
    
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
    
    # Метаданные
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Дополнительные поля
    average_rating = Column(Float, default=0.0)
    total_rides = Column(Integer, default=0)
    cancelled_rides = Column(Integer, default=0)
    
    # История изменений (JSON)
    profile_history = Column(JSON, default=list)

    # Отношения для рейтингов и отзывов
    ratings_given = relationship("Rating", foreign_keys="Rating.from_user_id", back_populates="from_user")
    ratings_received = relationship("Rating", foreign_keys="Rating.target_user_id", back_populates="target_user")
    reviews_given = relationship("Review", foreign_keys="Review.from_user_id", back_populates="from_user")
    reviews_received = relationship("Review", foreign_keys="Review.target_user_id", back_populates="target_user")
    
    # Отношения для платежей
    payments = relationship("Payment", back_populates="user")

class ProfileChangeLog(Base):
    __tablename__ = 'profile_change_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    field_name = Column(String, nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_at = Column(DateTime, default=func.now())
    changed_by = Column(String, default="user")  # user, admin, system 