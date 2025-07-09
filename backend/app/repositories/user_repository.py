from sqlalchemy.orm import Session
from typing import Optional, List
from fastapi import HTTPException, status
from ..models.user import User, ProfileChangeLog
from ..interfaces.auth import IUserRepository
from ..utils.logger import get_logger, db_logger

logger = get_logger("user_repository")

class UserRepository(IUserRepository):
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def find_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Найти пользователя по Telegram ID"""
        try:
            return self.db.query(User).filter(User.telegram_id == telegram_id).first()
        except Exception as e:
            logger.error(f"Ошибка поиска пользователя по Telegram ID {telegram_id}: {str(e)}")
            raise
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        """Найти пользователя по ID"""
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Ошибка поиска пользователя по ID {user_id}: {str(e)}")
            raise
    
    def save(self, user: User) -> User:
        """Сохранить пользователя"""
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка сохранения пользователя: {str(e)}")
            raise
    
    def update(self, user: User) -> User:
        """Обновить пользователя"""
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка обновления пользователя {user.id}: {str(e)}")
            raise
    
    def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        try:
            user = self.find_by_id(user_id)
            if not user:
                return False
            
            self.db.delete(user)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка удаления пользователя {user_id}: {str(e)}")
            raise
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Найти всех пользователей с пагинацией"""
        try:
            return self.db.query(User).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Ошибка поиска всех пользователей: {str(e)}")
            raise
    
    def find_active_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Найти активных пользователей"""
        try:
            return self.db.query(User).filter(User.is_active == True).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Ошибка поиска активных пользователей: {str(e)}")
            raise
    
    def find_drivers(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Найти водителей"""
        try:
            return self.db.query(User).filter(User.is_driver == True).limit(limit).offset(offset).all()
        except Exception as e:
            logger.error(f"Ошибка поиска водителей: {str(e)}")
            raise
    
    def add_profile_change_log(self, user_id: int, field_name: str, old_value: str, new_value: str, changed_by: str = "user"):
        """Добавить запись в лог изменений профиля"""
        try:
            change_log = ProfileChangeLog(
                user_id=user_id,
                field_name=field_name,
                old_value=old_value,
                new_value=new_value,
                changed_by=changed_by
            )
            self.db.add(change_log)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка добавления записи в лог изменений: {str(e)}")
            raise
    
    def get_profile_history(self, user_id: int, limit: int = 100) -> List[ProfileChangeLog]:
        """Получить историю изменений профиля"""
        try:
            return self.db.query(ProfileChangeLog).filter(
                ProfileChangeLog.user_id == user_id
            ).order_by(ProfileChangeLog.changed_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Ошибка получения истории профиля {user_id}: {str(e)}")
            raise 