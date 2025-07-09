import os
from typing import List, Optional
from pydantic import BaseSettings, Field
from functools import lru_cache

class Settings(BaseSettings):
    """Основные настройки приложения"""
    
    # Основная информация
    app_name: str = Field(default="Pax Backend", env="APP_NAME")
    version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="production", env="ENVIRONMENT")
    
    # API настройки
    api_prefix: str = Field(default="/api", env="API_PREFIX")
    cors_origins: List[str] = Field(default=[], env="CORS_ORIGINS")
    
    # Логирование
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # База данных
    database_url: str = Field(env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Безопасность
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Telegram
    telegram_bot_token: str = Field(env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_url: Optional[str] = Field(default=None, env="TELEGRAM_WEBHOOK_URL")
    
    # Файлы
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    # Мониторинг
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=8001, env="METRICS_PORT")
    
    # Кэширование
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1 час
    
    # Уведомления
    notification_queue_size: int = Field(default=1000, env="NOTIFICATION_QUEUE_SIZE")
    
    # Модерация
    auto_moderation: bool = Field(default=True, env="AUTO_MODERATION")
    moderation_threshold: float = Field(default=0.7, env="MODERATION_THRESHOLD")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Получение настроек с кэшированием"""
    return Settings()

# Глобальный экземпляр настроек
settings = get_settings() 