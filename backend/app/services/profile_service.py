from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from ..models.user import User, ProfileChangeLog
from ..schemas.user import UserRead, UserUpdate
from ..utils.error_handler import error_handler
from ..utils.logger import get_logger
from ..validators.data_validator import DataValidator

logger = get_logger("profile_service")

class ProfileService:
    """Сервис для работы с профилями пользователей"""
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = DataValidator()
    
    @error_handler.handle_database_operation("get_profile")
    def get_profile(self, user_id: int) -> Dict[str, Any]:
        """Получение профиля пользователя"""
        try:
            # Получаем пользователя с полной информацией
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.warning(f"Попытка получения профиля несуществующего пользователя: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Формируем полный профиль
            profile_data = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "full_name": user.full_name,
                "phone": user.phone,
                "email": user.email,
                "birth_date": user.birth_date.isoformat() if user.birth_date else None,
                "city": user.city,
                "avatar_url": user.avatar_url,
                "is_driver": user.is_driver,
                "is_active": user.is_active,
                "average_rating": float(user.average_rating) if user.average_rating else 0.0,
                "total_rides": user.total_rides or 0,
                "total_reviews": user.total_reviews or 0,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "privacy_policy_accepted": user.privacy_policy_accepted,
                "privacy_policy_accepted_at": user.privacy_policy_accepted_at.isoformat() if user.privacy_policy_accepted_at else None
            }
            
            # Добавляем водительские данные если пользователь водитель
            if user.is_driver and user.driver_data:
                profile_data["driver_data"] = {
                    "driver_license_number": user.driver_data.get("driver_license_number"),
                    "driver_license_photo_url": user.driver_data.get("driver_license_photo_url"),
                    "car_model": user.driver_data.get("car_model"),
                    "car_year": user.driver_data.get("car_year"),
                    "car_color": user.driver_data.get("car_color"),
                    "car_plate": user.driver_data.get("car_plate"),
                    "car_photo_url": user.driver_data.get("car_photo_url"),
                    "verified": user.driver_data.get("verified", False)
                }
            
            logger.info(f"Профиль пользователя {user_id} успешно получен")
            return profile_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения профиля пользователя {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка получения профиля"
            )
    
    @error_handler.handle_database_operation("update_profile")
    def update_profile(self, user_id: int, profile_data: UserUpdate) -> Dict[str, Any]:
        """Обновление профиля пользователя"""
        try:
            # Получаем пользователя
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                logger.warning(f"Попытка обновления профиля несуществующего пользователя: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Валидируем данные
            self._validate_profile_data(profile_data)
            
            # Сохраняем старые значения для логирования
            old_values = {}
            new_values = {}
            
            # Обновляем поля пользователя
            for field, value in profile_data.dict(exclude_unset=True).items():
                if hasattr(user, field):
                    old_value = getattr(user, field)
                    old_values[field] = str(old_value) if old_value is not None else None
                    
                    # Валидируем специальные поля
                    if field == "full_name" and value:
                        value = self.validator.validate_full_name(value)
                    elif field == "phone" and value:
                        value = self.validator.validate_phone(value)
                    elif field == "birth_date" and value:
                        value = self.validator.validate_birth_date(value)
                    
                    setattr(user, field, value)
                    new_values[field] = str(value) if value is not None else None
            
            # Обновляем время изменения
            user.updated_at = datetime.now()
            
            # Сохраняем изменения
            self.db.commit()
            
            # Логируем изменения
            self._log_profile_changes(user_id, old_values, new_values)
            
            logger.info(f"Профиль пользователя {user_id} успешно обновлен")
            
            # Возвращаем обновленный профиль
            return self.get_profile(user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка обновления профиля пользователя {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка обновления профиля"
            )
    
    def _validate_profile_data(self, profile_data: UserUpdate) -> None:
        """Валидация данных профиля"""
        try:
            # Валидируем имя если обновляется
            if profile_data.full_name is not None:
                self.validator.validate_full_name(profile_data.full_name)
            
            # Валидируем телефон если обновляется
            if profile_data.phone is not None:
                self.validator.validate_phone(profile_data.phone)
            
            # Валидируем дату рождения если обновляется
            if profile_data.birth_date is not None:
                self.validator.validate_birth_date(profile_data.birth_date)
            
            # Валидируем email если обновляется
            if profile_data.email is not None:
                if not self.validator.email_pattern.match(profile_data.email):
                    raise ValueError("Некорректный формат email")
            
            # Валидируем город если обновляется
            if profile_data.city is not None:
                if len(profile_data.city.strip()) < 2:
                    raise ValueError("Название города должно содержать минимум 2 символа")
            
            # Валидируем URL аватара если обновляется
            if profile_data.avatar_url is not None:
                if not self.validator.url_pattern.match(profile_data.avatar_url):
                    raise ValueError("Некорректный URL аватара")
            
        except ValueError as e:
            logger.warning(f"Ошибка валидации данных профиля: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
    
    def _log_profile_changes(self, user_id: int, old_values: Dict[str, str], new_values: Dict[str, str]) -> None:
        """Логирование изменений профиля"""
        try:
            for field, new_value in new_values.items():
                old_value = old_values.get(field)
                
                # Логируем только если значение изменилось
                if old_value != new_value:
                    change_log = ProfileChangeLog(
                        user_id=user_id,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        changed_at=datetime.now(),
                        changed_by=user_id  # Пользователь изменил свой профиль
                    )
                    self.db.add(change_log)
            
            self.db.commit()
            logger.info(f"Изменения профиля пользователя {user_id} залогированы")
            
        except Exception as e:
            logger.error(f"Ошибка логирования изменений профиля {user_id}: {str(e)}")
            # Не прерываем основной процесс из-за ошибки логирования
    
    def get_profile_history(self, user_id: int, limit: int = 50) -> list:
        """Получение истории изменений профиля"""
        try:
            # Проверяем существование пользователя
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Получаем историю изменений
            logs = self.db.query(ProfileChangeLog).filter(
                ProfileChangeLog.user_id == user_id
            ).order_by(ProfileChangeLog.changed_at.desc()).limit(limit).all()
            
            history = [
                {
                    "field_name": log.field_name,
                    "old_value": log.old_value,
                    "new_value": log.new_value,
                    "changed_at": log.changed_at.isoformat(),
                    "changed_by": log.changed_by
                }
                for log in logs
            ]
            
            logger.info(f"Получена история профиля пользователя {user_id}: {len(history)} записей")
            return history
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения истории профиля {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка получения истории профиля"
            )
    
    def delete_profile(self, user_id: int) -> bool:
        """Удаление профиля пользователя (мягкое удаление)"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Мягкое удаление - деактивируем пользователя
            user.is_active = False
            user.updated_at = datetime.now()
            
            self.db.commit()
            
            logger.info(f"Профиль пользователя {user_id} деактивирован")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка удаления профиля пользователя {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка удаления профиля"
            )
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики пользователя"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            stats = {
                "user_id": user_id,
                "total_rides": user.total_rides or 0,
                "average_rating": float(user.average_rating) if user.average_rating else 0.0,
                "total_reviews": user.total_reviews or 0,
                "is_driver": user.is_driver,
                "is_active": user.is_active,
                "days_since_registration": (datetime.now() - user.created_at).days,
                "last_login_days_ago": (datetime.now() - user.last_login_at).days if user.last_login_at else None
            }
            
            logger.info(f"Статистика пользователя {user_id} получена")
            return stats
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения статистики пользователя {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка получения статистики"
            ) 