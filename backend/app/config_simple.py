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
    """Упрощенные настройки без проблемных переменных окружения"""
    
    # Основные настройки
    app_name: str = "Ride Sharing API"
    version: str = "1.0.0"
    debug: bool = True
    
    # База данных
    database_url: str = "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@localhost/paxmain"
    
    # Telegram Bot
    telegram_bot_token: str = "8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA"
    telegram_bot_username: str = "paxdemobot"
    
    # Безопасность
    secret_key: str = "8f3b2c1e-4a5d-11ee-be56-0242ac120002"
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
    
    # Переменные окружения для разработки
    environment: str = "development"
    
    # Redis (для кэширования и сессий)
    redis_url: Optional[str] = None
    
    # Email (для уведомлений)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    


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