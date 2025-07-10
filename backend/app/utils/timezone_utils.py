"""
Утилиты для работы с timezone и согласованности времени
Обеспечивает единообразную работу с датами и временем в приложении
"""

import pytz
from datetime import datetime, timezone
from typing import Optional, Union
from ..config.settings import settings

class TimezoneManager:
    """Менеджер для работы с timezone"""
    
    def __init__(self):
        self.default_timezone = pytz.timezone(settings.timezone)
        self.use_utc = settings.use_utc
    
    def get_current_timezone(self) -> pytz.timezone:
        """Получение текущего timezone"""
        return self.default_timezone
    
    def now(self, timezone_name: Optional[str] = None) -> datetime:
        """Получение текущего времени в указанном timezone"""
        if self.use_utc:
            return datetime.now(timezone.utc)
        
        if timezone_name:
            tz = pytz.timezone(timezone_name)
        else:
            tz = self.default_timezone
        
        return datetime.now(tz)
    
    def localize_datetime(self, dt: datetime, timezone_name: Optional[str] = None) -> datetime:
        """Локализация datetime в указанный timezone"""
        if dt.tzinfo is None:
            # Если datetime наивный (без timezone), считаем что он в UTC
            dt = dt.replace(tzinfo=timezone.utc)
        
        if timezone_name:
            target_tz = pytz.timezone(timezone_name)
        else:
            target_tz = self.default_timezone
        
        return dt.astimezone(target_tz)
    
    def format_datetime(self, dt: datetime, format_str: Optional[str] = None) -> str:
        """Форматирование datetime в строку"""
        if format_str is None:
            format_str = settings.datetime_format
        
        # Локализуем datetime если нужно
        if not self.use_utc:
            dt = self.localize_datetime(dt)
        
        return dt.strftime(format_str)
    
    def parse_datetime(self, date_string: str, format_str: Optional[str] = None) -> datetime:
        """Парсинг строки в datetime"""
        if format_str is None:
            format_str = settings.datetime_format
        
        dt = datetime.strptime(date_string, format_str)
        
        # Если используем UTC, добавляем timezone
        if self.use_utc:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = self.default_timezone.localize(dt)
        
        return dt
    
    def to_utc(self, dt: datetime) -> datetime:
        """Конвертация datetime в UTC"""
        if dt.tzinfo is None:
            # Если datetime наивный, считаем что он в локальном timezone
            dt = self.default_timezone.localize(dt)
        
        return dt.astimezone(timezone.utc)
    
    def from_utc(self, dt: datetime, target_timezone: Optional[str] = None) -> datetime:
        """Конвертация datetime из UTC в указанный timezone"""
        if dt.tzinfo is None:
            # Если datetime наивный, считаем что он в UTC
            dt = dt.replace(tzinfo=timezone.utc)
        
        if target_timezone:
            target_tz = pytz.timezone(target_timezone)
        else:
            target_tz = self.default_timezone
        
        return dt.astimezone(target_tz)
    
    def get_timezone_offset(self, timezone_name: Optional[str] = None) -> int:
        """Получение смещения timezone в секундах"""
        if timezone_name:
            tz = pytz.timezone(timezone_name)
        else:
            tz = self.default_timezone
        
        now = datetime.now(tz)
        return int(now.utcoffset().total_seconds())
    
    def is_dst(self, timezone_name: Optional[str] = None) -> bool:
        """Проверка на летнее время"""
        if timezone_name:
            tz = pytz.timezone(timezone_name)
        else:
            tz = self.default_timezone
        
        now = datetime.now(tz)
        return bool(now.dst())
    
    def get_available_timezones(self) -> list:
        """Получение списка доступных timezone"""
        return pytz.all_timezones
    
    def validate_timezone(self, timezone_name: str) -> bool:
        """Валидация timezone"""
        try:
            pytz.timezone(timezone_name)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False

# Глобальный экземпляр менеджера timezone
timezone_manager = TimezoneManager()

# Утилитарные функции для удобного использования
def get_current_datetime(timezone_name: Optional[str] = None) -> datetime:
    """Получение текущего datetime"""
    return timezone_manager.now(timezone_name)

def format_datetime(dt: datetime, format_str: Optional[str] = None) -> str:
    """Форматирование datetime в строку"""
    return timezone_manager.format_datetime(dt, format_str)

def parse_datetime(date_string: str, format_str: Optional[str] = None) -> datetime:
    """Парсинг строки в datetime"""
    return timezone_manager.parse_datetime(date_string, format_str)

def to_utc(dt: datetime) -> datetime:
    """Конвертация datetime в UTC"""
    return timezone_manager.to_utc(dt)

def from_utc(dt: datetime, target_timezone: Optional[str] = None) -> datetime:
    """Конвертация datetime из UTC в указанный timezone"""
    return timezone_manager.from_utc(dt, target_timezone)

def localize_datetime(dt: datetime, timezone_name: Optional[str] = None) -> datetime:
    """Локализация datetime в указанный timezone"""
    return timezone_manager.localize_datetime(dt, timezone_name)

def get_timezone_offset(timezone_name: Optional[str] = None) -> int:
    """Получение смещения timezone в секундах"""
    return timezone_manager.get_timezone_offset(timezone_name)

def is_dst(timezone_name: Optional[str] = None) -> bool:
    """Проверка на летнее время"""
    return timezone_manager.is_dst(timezone_name)

def validate_timezone(timezone_name: str) -> bool:
    """Валидация timezone"""
    return timezone_manager.validate_timezone(timezone_name)

def get_available_timezones() -> list:
    """Получение списка доступных timezone"""
    return timezone_manager.get_available_timezones()

# Функции для работы с датами в API
def api_datetime_to_utc(dt: Union[str, datetime]) -> datetime:
    """Конвертация datetime из API в UTC для сохранения в БД"""
    if isinstance(dt, str):
        dt = parse_datetime(dt)
    
    return to_utc(dt)

def utc_to_api_datetime(dt: datetime, target_timezone: Optional[str] = None) -> str:
    """Конвертация datetime из UTC в формат для API"""
    if target_timezone:
        dt = from_utc(dt, target_timezone)
    else:
        dt = from_utc(dt)
    
    return format_datetime(dt)

def get_user_timezone(user_timezone: Optional[str] = None) -> str:
    """Получение timezone пользователя"""
    if user_timezone and validate_timezone(user_timezone):
        return user_timezone
    return settings.timezone

# Функции для работы с временными интервалами
def is_datetime_in_future(dt: datetime, buffer_minutes: int = 0) -> bool:
    """Проверка что datetime в будущем"""
    now = get_current_datetime()
    if buffer_minutes > 0:
        from datetime import timedelta
        now += timedelta(minutes=buffer_minutes)
    
    return dt > now

def is_datetime_in_past(dt: datetime, buffer_minutes: int = 0) -> bool:
    """Проверка что datetime в прошлом"""
    now = get_current_datetime()
    if buffer_minutes > 0:
        from datetime import timedelta
        now -= timedelta(minutes=buffer_minutes)
    
    return dt < now

def get_datetime_difference(dt1: datetime, dt2: datetime) -> int:
    """Получение разности между datetime в минутах"""
    if dt1.tzinfo is None:
        dt1 = localize_datetime(dt1)
    if dt2.tzinfo is None:
        dt2 = localize_datetime(dt2)
    
    diff = abs(dt1 - dt2)
    return int(diff.total_seconds() / 60)

def add_minutes_to_datetime(dt: datetime, minutes: int) -> datetime:
    """Добавление минут к datetime"""
    from datetime import timedelta
    return dt + timedelta(minutes=minutes)

def subtract_minutes_from_datetime(dt: datetime, minutes: int) -> datetime:
    """Вычитание минут из datetime"""
    from datetime import timedelta
    return dt - timedelta(minutes=minutes) 