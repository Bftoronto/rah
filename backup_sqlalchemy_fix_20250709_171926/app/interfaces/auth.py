from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..schemas.user import UserCreate, UserUpdate, UserRead, PrivacyPolicyAccept
from ..models.user import User

class IAuthService(ABC):
    """Интерфейс для сервиса аутентификации"""
    
    @abstractmethod
    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    def create_user(self, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        pass
    
    @abstractmethod
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Обновить данные пользователя"""
        pass
    
    @abstractmethod
    def accept_privacy_policy(self, user_id: int, privacy_data: PrivacyPolicyAccept) -> User:
        """Принять пользовательское соглашение"""
        pass
    
    @abstractmethod
    def verify_telegram_user(self, telegram_data: Dict[str, Any]) -> Optional[User]:
        """Верификация пользователя через Telegram"""
        pass
    
    @abstractmethod
    def get_profile_history(self, user_id: int) -> list:
        """Получить историю изменений профиля"""
        pass

class IUserRepository(ABC):
    """Интерфейс для репозитория пользователей"""
    
    @abstractmethod
    def find_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Найти пользователя по Telegram ID"""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Найти пользователя по ID"""
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Сохранить пользователя"""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Обновить пользователя"""
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        """Найти всех пользователей с пагинацией"""
        pass

class IValidator(ABC):
    """Интерфейс для валидации данных"""
    
    @abstractmethod
    def validate_telegram_data(self, data: Dict[str, Any]) -> bool:
        """Валидация данных Telegram"""
        pass
    
    @abstractmethod
    def validate_user_data(self, user_data: UserCreate) -> bool:
        """Валидация данных пользователя"""
        pass
    
    @abstractmethod
    def validate_user_update(self, user_data: UserUpdate) -> bool:
        """Валидация обновления пользователя"""
        pass

class ISecurityService(ABC):
    """Интерфейс для сервиса безопасности"""
    
    @abstractmethod
    def verify_telegram_signature(self, data: Dict[str, Any]) -> bool:
        """Верификация подписи Telegram"""
        pass
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Хеширование пароля"""
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        pass
    
    @abstractmethod
    def generate_token(self, user_id: int) -> str:
        """Генерация токена"""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[int]:
        """Проверка токена"""
        pass 