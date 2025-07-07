from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from ..database import Base
import uuid

class NotificationLog(Base):
    __tablename__ = 'notification_logs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=False)
    notification_type = Column(String, nullable=False)
    title = Column(String)
    message = Column(Text)
    sent_at = Column(DateTime, default=func.now())
    success = Column(Boolean, default=False)
    error_message = Column(Text)
    telegram_response = Column(JSON)
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )

class NotificationSettings(Base):
    __tablename__ = 'notification_settings'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)
    ride_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    reminder_notifications = Column(Boolean, default=True)
    marketing_notifications = Column(Boolean, default=False)
    quiet_hours_start = Column(String)  # "22:00"
    quiet_hours_end = Column(String)    # "08:00"
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 