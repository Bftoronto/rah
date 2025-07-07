from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from datetime import datetime
import logging
from typing import Optional, Dict, Any
from ..database import get_db
from ..models.user import User, ProfileChangeLog
from ..schemas.user import UserCreate, UserUpdate, UserRead, PrivacyPolicyAccept
from ..utils.security import verify_telegram_data
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)
security = HTTPBearer()

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        try:
            # Проверяем, не существует ли уже пользователь с таким Telegram ID
            existing_user = self.get_user_by_telegram_id(str(user_data.telegram_id))
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким Telegram ID уже существует"
                )
            
            # Создаем нового пользователя
            db_user = User(
                telegram_id=str(user_data.telegram_id),
                username=user_data.username,
                full_name=user_data.full_name,
                phone=user_data.phone,
                birth_date=user_data.birth_date,
                city=user_data.city,
                avatar_url=user_data.avatar_url,
                is_driver=user_data.is_driver,
                car_brand=user_data.car_brand,
                car_model=user_data.car_model,
                car_year=user_data.car_year,
                car_color=user_data.car_color,
                driver_license_number=user_data.driver_license_number,
                driver_license_photo_url=user_data.driver_license_photo_url,
                car_photo_url=user_data.car_photo_url,
                privacy_policy_accepted=user_data.privacy_policy_accepted,
                privacy_policy_accepted_at=datetime.now() if user_data.privacy_policy_accepted else None,
                privacy_policy_version=user_data.privacy_policy_version
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            logger.info(f"Создан новый пользователь: {db_user.telegram_id}")
            return db_user
            
        except HTTPException:
            self.db.rollback()
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ошибка целостности данных при создании пользователя: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с такими данными уже существует"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Неожиданная ошибка при создании пользователя: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка создания пользователя"
            )
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Обновить данные пользователя"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Логируем изменения
            changes = []
            
            # Обновляем основные поля
            if user_data.phone is not None and user_data.phone != user.phone:
                changes.append(("phone", user.phone, user_data.phone))
                user.phone = user_data.phone
            
            if user_data.full_name is not None and user_data.full_name != user.full_name:
                changes.append(("full_name", user.full_name, user_data.full_name))
                user.full_name = user_data.full_name
            
            if user_data.birth_date is not None and user_data.birth_date != user.birth_date:
                changes.append(("birth_date", str(user.birth_date), str(user_data.birth_date)))
                user.birth_date = user_data.birth_date
            
            if user_data.city is not None and user_data.city != user.city:
                changes.append(("city", user.city, user_data.city))
                user.city = user_data.city
            
            if user_data.avatar_url is not None and user_data.avatar_url != user.avatar_url:
                changes.append(("avatar_url", user.avatar_url, user_data.avatar_url))
                user.avatar_url = user_data.avatar_url
            
            # Обновляем водительские данные
            if user_data.driver_data:
                if user_data.driver_data.car_brand != user.car_brand:
                    changes.append(("car_brand", user.car_brand, user_data.driver_data.car_brand))
                    user.car_brand = user_data.driver_data.car_brand
                
                if user_data.driver_data.car_model != user.car_model:
                    changes.append(("car_model", user.car_model, user_data.driver_data.car_model))
                    user.car_model = user_data.driver_data.car_model
                
                if user_data.driver_data.car_year != user.car_year:
                    changes.append(("car_year", str(user.car_year), str(user_data.driver_data.car_year)))
                    user.car_year = user_data.driver_data.car_year
                
                if user_data.driver_data.car_color != user.car_color:
                    changes.append(("car_color", user.car_color, user_data.driver_data.car_color))
                    user.car_color = user_data.driver_data.car_color
                
                if user_data.driver_data.driver_license_number != user.driver_license_number:
                    changes.append(("driver_license_number", user.driver_license_number, user_data.driver_data.driver_license_number))
                    user.driver_license_number = user_data.driver_data.driver_license_number
                
                if user_data.driver_data.driver_license_photo_url != user.driver_license_photo_url:
                    changes.append(("driver_license_photo_url", user.driver_license_photo_url, user_data.driver_data.driver_license_photo_url))
                    user.driver_license_photo_url = user_data.driver_data.driver_license_photo_url
                
                if user_data.driver_data.car_photo_url != user.car_photo_url:
                    changes.append(("car_photo_url", user.car_photo_url, user_data.driver_data.car_photo_url))
                    user.car_photo_url = user_data.driver_data.car_photo_url
                
                # Если есть водительские данные, помечаем как водителя
                if not user.is_driver:
                    user.is_driver = True
                    changes.append(("is_driver", "False", "True"))
            
            # Сохраняем изменения в профиле
            if changes:
                user.updated_at = datetime.now()
                
                # Добавляем записи в лог изменений
                for field_name, old_value, new_value in changes:
                    change_log = ProfileChangeLog(
                        user_id=user_id,
                        field_name=field_name,
                        old_value=old_value,
                        new_value=new_value,
                        changed_by="user"
                    )
                    self.db.add(change_log)
                
                # Обновляем историю в профиле
                if not user.profile_history:
                    user.profile_history = []
                
                for field_name, old_value, new_value in changes:
                    user.profile_history.append({
                        "field_name": field_name,
                        "old_value": old_value,
                        "new_value": new_value,
                        "changed_at": datetime.now().isoformat(),
                        "changed_by": "user"
                    })
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Обновлен профиль пользователя: {user.telegram_id}")
            return user
            
        except HTTPException:
            self.db.rollback()
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ошибка целостности данных при обновлении пользователя: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Конфликт данных при обновлении профиля"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Неожиданная ошибка при обновлении пользователя: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка обновления пользователя"
            )
    
    def accept_privacy_policy(self, user_id: int, privacy_data: PrivacyPolicyAccept) -> User:
        """Принять пользовательское соглашение"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            if privacy_data.accepted:
                user.privacy_policy_accepted = True
                user.privacy_policy_accepted_at = datetime.now()
                user.privacy_policy_version = privacy_data.version
                
                self.db.commit()
                self.db.refresh(user)
                
                logger.info(f"Пользователь {user.telegram_id} принял соглашение версии {privacy_data.version}")
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Необходимо принять пользовательское соглашение"
                )
                
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Неожиданная ошибка при принятии соглашения: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка принятия соглашения"
            )
    
    def verify_telegram_user(self, telegram_data: Dict[str, Any]) -> Optional[User]:
        """Верификация пользователя через Telegram"""
        try:
            # Проверяем подпись Telegram
            if not verify_telegram_data(telegram_data):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверная подпись Telegram"
                )
            
            telegram_id = str(telegram_data.get('id'))
            if not telegram_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Отсутствует Telegram ID"
                )
            
            # Ищем пользователя
            user = self.get_user_by_telegram_id(telegram_id)
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при верификации Telegram: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка верификации Telegram"
            )
    
    def get_profile_history(self, user_id: int) -> list:
        """Получить историю изменений профиля"""
        try:
            logs = self.db.query(ProfileChangeLog).filter(
                ProfileChangeLog.user_id == user_id
            ).order_by(ProfileChangeLog.changed_at.desc()).all()
            
            return [
                {
                    "field_name": log.field_name,
                    "old_value": log.old_value,
                    "new_value": log.new_value,
                    "changed_at": log.changed_at,
                    "changed_by": log.changed_by
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения истории профиля: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка получения истории профиля"
            )

    def register(self, user_data):
        # TODO: Реализация регистрации
        pass

    def login(self, credentials):
        # TODO: Реализация логина
        pass


# Зависимость для получения текущего пользователя
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получить текущего пользователя из токена"""
    try:
        # Для демо версии просто возвращаем первого пользователя
        # В продакшене здесь должна быть проверка JWT токена
        user = db.query(User).filter(User.is_active == True).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения текущего пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось аутентифицировать пользователя"
        )


