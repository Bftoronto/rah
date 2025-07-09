import os
import logging
from typing import Optional, List

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleSettings:
    """Упрощенные настройки с поддержкой переменных окружения"""
    
    # Основные настройки
    app_name: str = "Ride Sharing API"
    version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # База данных - приоритет переменным окружения
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://user:password@localhost/paxmain"
    )
    
    # Telegram Bot
    telegram_bot_token: str = os.getenv(
        "TELEGRAM_BOT_TOKEN", 
        ""
    )
    telegram_bot_username: str = os.getenv("TELEGRAM_BOT_USERNAME", "paxdemobot")
    
    # Безопасность
    secret_key: str = os.getenv(
        "SECRET_KEY", 
        "CHANGE_THIS_IN_PRODUCTION"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Загрузка файлов
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/gif"]
    
    # CORS
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Логирование
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE")
    
    # Переменные окружения для разработки
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Redis (для кэширования и сессий)
    redis_url: Optional[str] = os.getenv("REDIS_URL")
    
    # Email (для уведомлений)
    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"

# Создание экземпляра настроек
settings = SimpleSettings()

# Проверка обязательных переменных окружения
def validate_settings():
    """Проверка обязательных настроек"""
    required_settings = [
        "database_url"
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