from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """Настройки базы данных"""
    
    url: str = Field(env="DATABASE_URL")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    pool_recycle: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    
    # Настройки для разработки
    echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Настройки для тестов
    test_url: Optional[str] = Field(default=None, env="TEST_DATABASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False 