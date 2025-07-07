import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    # Основные настройки
    app_name: str = "Ride Sharing API"
    version: str = "1.0.0"
    debug: bool = False
    
    # База данных
    database_url: str = "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain"
    
    # Telegram Bot
    telegram_bot_token: Optional[str] = None
    telegram_bot_username: Optional[str] = None
    
    # Безопасность
    secret_key: str = "SECRET_KEY=8f3b2c1e-4a5d-11ee-be56-0242ac120002"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Загрузка файлов
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/gif"]
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Логирование
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # Redis (для кэширования и сессий)
    redis_url: Optional[str] = None
    
    # Email (для уведомлений)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # Платежи
    payment_gateway_url: Optional[str] = None
    payment_gateway_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Создание экземпляра настроек
settings = Settings()

# Проверка обязательных переменных окружения
def validate_settings():
    """Проверка обязательных настроек"""
    required_settings = [
        "database_url",
        "telegram_bot_token"
    ]
    
    missing_settings = []
    for setting in required_settings:
        if not getattr(settings, setting, None):
            missing_settings.append(setting)
    
    if missing_settings:
        raise ValueError(f"Отсутствуют обязательные настройки: {', '.join(missing_settings)}")

# Валидация настроек безопасности
def validate_security_settings():
    """Проверка настроек безопасности"""
    if settings.secret_key == "your-secret-key-here":
        logger.warning("ВНИМАНИЕ: Используется стандартный secret_key. Измените его в продакшене!")
    
    if settings.debug:
        logger.warning("ВНИМАНИЕ: Режим отладки включен. Отключите в продакшене!")
    
    if "*" in settings.cors_origins:
        logger.warning("ВНИМАНИЕ: CORS настроен на все домены. Ограничьте в продакшене!")

# Валидация настроек при импорте
try:
    validate_settings()
    validate_security_settings()
except ValueError as e:
    logger.error(f"Ошибка конфигурации: {e}")
    logger.error("Убедитесь, что все обязательные переменные окружения установлены") 