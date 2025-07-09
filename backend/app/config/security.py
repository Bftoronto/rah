from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings

class SecuritySettings(BaseSettings):
    """Настройки безопасности"""
    
    # JWT
    secret_key: str = Field(env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Пароли
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_require_special: bool = Field(default=True, env="PASSWORD_REQUIRE_SPECIAL")
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 час
    
    # CORS
    allowed_origins: List[str] = Field(default=[], env="ALLOWED_ORIGINS")
    allowed_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE"], env="ALLOWED_METHODS")
    allowed_headers: List[str] = Field(default=["*"], env="ALLOWED_HEADERS")
    
    # Telegram
    telegram_bot_token: str = Field(env="TELEGRAM_BOT_TOKEN")
    telegram_webhook_secret: str = Field(env="TELEGRAM_WEBHOOK_SECRET")
    
    # Файлы
    allowed_file_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "application/pdf"],
        env="ALLOWED_FILE_TYPES"
    )
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False 