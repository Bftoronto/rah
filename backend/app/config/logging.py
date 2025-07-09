from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class LoggingSettings(BaseSettings):
    """Настройки логирования"""
    
    # Уровни логирования
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    
    # Файлы логов
    app_log_file: str = Field(default="logs/app.log", env="APP_LOG_FILE")
    error_log_file: str = Field(default="logs/errors.log", env="ERROR_LOG_FILE")
    access_log_file: str = Field(default="logs/access.log", env="ACCESS_LOG_FILE")
    
    # Ротация логов
    max_file_size: int = Field(default=10 * 1024 * 1024, env="LOG_MAX_FILE_SIZE")  # 10MB
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # Структурированное логирование
    enable_structured_logging: bool = Field(default=True, env="ENABLE_STRUCTURED_LOGGING")
    include_timestamp: bool = Field(default=True, env="LOG_INCLUDE_TIMESTAMP")
    include_level: bool = Field(default=True, env="LOG_INCLUDE_LEVEL")
    include_module: bool = Field(default=True, env="LOG_INCLUDE_MODULE")
    
    # Фильтрация
    exclude_paths: List[str] = Field(
        default=["/health", "/metrics", "/favicon.ico"],
        env="LOG_EXCLUDE_PATHS"
    )
    
    # Мониторинг
    enable_performance_logging: bool = Field(default=True, env="ENABLE_PERFORMANCE_LOGGING")
    enable_security_logging: bool = Field(default=True, env="ENABLE_SECURITY_LOGGING")
    enable_database_logging: bool = Field(default=True, env="ENABLE_DATABASE_LOGGING")
    
    class Config:
        env_file = ".env"
        case_sensitive = False 