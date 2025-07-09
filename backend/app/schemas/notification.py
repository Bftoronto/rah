from pydantic import BaseModel, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

class NotificationCreate(BaseModel):
    user_id: int
    title: Optional[str] = None
    message: Optional[str] = None
    notification_type: str = "info"
    ride_data: Optional[Dict[str, Any]] = None
    
    @validator('notification_type')
    def validate_notification_type(cls, v):
        allowed_types = [
            "info", "success", "warning", "error", "security",
            "new_ride", "ride_reminder", "ride_cancelled", 
            "booking_confirmed", "new_passenger"
        ]
        if v not in allowed_types:
            raise ValueError(f"Неподдерживаемый тип уведомления: {v}")
        return v

class BulkNotificationCreate(BaseModel):
    user_ids: List[int]
    title: str
    message: str
    notification_type: str = "info"
    
    @validator('user_ids')
    def validate_user_ids(cls, v):
        if not v:
            raise ValueError("Список пользователей не может быть пустым")
        if len(v) > 1000:
            raise ValueError("Максимум 1000 пользователей за раз")
        return v
    
    @validator('notification_type')
    def validate_notification_type(cls, v):
        allowed_types = ["info", "success", "warning", "error", "security"]
        if v not in allowed_types:
            raise ValueError(f"Неподдерживаемый тип уведомления: {v}")
        return v

class NotificationResponse(BaseModel):
    success: bool
    message: str
    notification_id: Optional[str] = None
    sent_at: Optional[datetime] = None

class NotificationSettings(BaseModel):
    user_id: int
    ride_notifications: bool = True
    system_notifications: bool = True
    reminder_notifications: bool = True
    marketing_notifications: bool = False
    quiet_hours_start: Optional[str] = None  # "22:00"
    quiet_hours_end: Optional[str] = None    # "08:00"
    email_notifications: bool = False
    push_notifications: bool = True
    
    @validator('quiet_hours_start', 'quiet_hours_end')
    def validate_time_format(cls, v):
        if v is not None:
            try:
                # Проверяем формат времени HH:MM
                if not re.match(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$', v):
                    raise ValueError('Неверный формат времени. Используйте HH:MM')
                hour, minute = map(int, v.split(':'))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError('Неверное время')
            except Exception:
                raise ValueError("Время должно быть в формате HH:MM")
        return v

class NotificationTemplate(BaseModel):
    name: str
    title: str
    message: str
    notification_type: str = "info"
    variables: List[str] = []
    
    @validator('variables')
    def validate_variables(cls, v):
        # Проверяем, что все переменные в сообщении определены
        return v

class NotificationStats(BaseModel):
    total_sent: int
    successful: int
    failed: int
    success_rate: float
    last_24h: int
    last_week: int
    last_month: int

class NotificationLog(BaseModel):
    id: str
    user_id: int
    notification_type: str
    title: Optional[str]
    message: Optional[str]
    sent_at: datetime
    success: bool
    error_message: Optional[str] = None
    telegram_response: Optional[Dict[str, Any]] = None

# Aliases for backward compatibility
NotificationRead = NotificationResponse
NotificationUpdate = NotificationCreate 