from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from datetime import datetime
import time
from typing import Optional, Dict, Any
from pydantic import ValidationError
from ..database import get_db
from ..models.user import User, ProfileChangeLog
from ..schemas.user import UserCreate, UserUpdate, UserRead, PrivacyPolicyAccept
from ..utils.security import verify_telegram_data
from ..utils.logger import get_logger, db_logger, security_logger, log_exception
from ..utils.jwt_auth import jwt_auth
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload

logger = get_logger("auth_service")
security = HTTPBearer()

class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Получить пользователя по Telegram ID с оптимизированным запросом"""
        start_time = time.time()
        try:
            # Оптимизированный запрос с выбором только необходимых полей
            user = self.db.query(User).filter(
                User.telegram_id == telegram_id
            ).options(
                # Загружаем связанные данные только при необходимости
                selectinload(User.rides_as_driver),
                selectinload(User.rides_as_passenger)
            ).first()
            
            duration_ms = (time.time() - start_time) * 1000
            db_logger.query_success("GET_USER_BY_TELEGRAM_ID", "users", 1 if user else 0, duration_ms)
            
            return user
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.query_error("GET_USER_BY_TELEGRAM_ID", "users", e)
            log_exception(logger, e, {"telegram_id": telegram_id})
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID с логированием"""
        start_time = time.time()
        try:
            db_logger.query_start("SELECT", "users", {"id": user_id})
            
            user = self.db.query(User).filter(User.id == user_id).first()
            
            duration_ms = (time.time() - start_time) * 1000
            db_logger.query_success("SELECT", "users", 1 if user else 0, duration_ms)
            
            if user:
                logger.debug(f"Пользователь найден по ID: {user_id}")
            else:
                logger.debug(f"Пользователь не найден по ID: {user_id}")
            return user
        except SQLAlchemyError as e:
            duration_ms = (time.time() - start_time) * 1000
            db_logger.query_error("SELECT", "users", e)
            logger.error(f"Ошибка базы данных при поиске пользователя по ID {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных"
            )
    
    def create_user(self, user_data: UserCreate) -> User:
        """Создать нового пользователя с улучшенной обработкой ошибок"""
        start_time = time.time()
        try:
            # Валидация входных данных
            if not user_data.telegram_id:
                security_logger.data_validation_error("telegram_id", None, "required")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Telegram ID обязателен"
                )
            
            # Проверяем, не существует ли уже пользователь с таким Telegram ID
            existing_user = self.get_user_by_telegram_id(str(user_data.telegram_id))
            if existing_user:
                security_logger.data_validation_error("telegram_id", user_data.telegram_id, "duplicate")
                logger.warning(f"Попытка создания пользователя с существующим Telegram ID: {user_data.telegram_id}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким Telegram ID уже существует"
                )
            
            db_logger.transaction_start("CREATE_USER")
            
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
            
            duration_ms = (time.time() - start_time) * 1000
            db_logger.transaction_commit("CREATE_USER", duration_ms)
            
            logger.info(f"Создан новый пользователь: {db_user.telegram_id} (ID: {db_user.id})")
            return db_user
            
        except HTTPException:
            self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000
            db_logger.transaction_rollback("CREATE_USER", Exception("HTTPException"))
            raise
        except IntegrityError as e:
            self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000
            db_logger.transaction_rollback("CREATE_USER", e)
            logger.error(f"Ошибка целостности данных при создании пользователя: {str(e)}")
            # Определяем тип ошибки целостности
            if "telegram_id" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким Telegram ID уже существует"
                )
            elif "phone" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с таким номером телефона уже существует"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Пользователь с такими данными уже существует"
                )
        except SQLAlchemyError as e:
            self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000
            db_logger.transaction_rollback("CREATE_USER", e)
            logger.error(f"Ошибка базы данных при создании пользователя: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных при создании пользователя"
            )
        except Exception as e:
            self.db.rollback()
            duration_ms = (time.time() - start_time) * 1000
            db_logger.transaction_rollback("CREATE_USER", e)
            log_exception(logger, e, {"telegram_id": user_data.telegram_id if user_data else None})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка создания пользователя"
            )
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Обновить данные пользователя с улучшенной обработкой ошибок"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Попытка обновления несуществующего пользователя: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Логируем изменения
            changes = []
            
            # Обновляем основные поля с валидацией
            if user_data.phone is not None and user_data.phone != user.phone:
                # Валидация номера телефона
                if user_data.phone and len(user_data.phone) < 10:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Некорректный номер телефона"
                    )
                changes.append(("phone", user.phone, user_data.phone))
                user.phone = user_data.phone
            
            if user_data.full_name is not None and user_data.full_name != user.full_name:
                # Валидация имени
                if len(user_data.full_name.strip()) < 2:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Имя должно содержать минимум 2 символа"
                    )
                changes.append(("full_name", user.full_name, user_data.full_name))
                user.full_name = user_data.full_name
            
            if user_data.birth_date is not None and user_data.birth_date != user.birth_date:
                # Валидация даты рождения
                if user_data.birth_date > datetime.now().date():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Дата рождения не может быть в будущем"
                    )
                changes.append(("birth_date", str(user.birth_date), str(user_data.birth_date)))
                user.birth_date = user_data.birth_date
            
            if user_data.city is not None and user_data.city != user.city:
                # Валидация города
                if len(user_data.city.strip()) < 2:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Название города должно содержать минимум 2 символа"
                    )
                changes.append(("city", user.city, user_data.city))
                user.city = user_data.city
            
            if user_data.avatar_url is not None and user_data.avatar_url != user.avatar_url:
                # Валидация URL аватара
                if user_data.avatar_url and not user_data.avatar_url.startswith(('http://', 'https://')):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Некорректный URL аватара"
                    )
                changes.append(("avatar_url", user.avatar_url, user_data.avatar_url))
                user.avatar_url = user_data.avatar_url
            
            # Обновляем водительские данные
            if user_data.driver_data:
                if user_data.driver_data.car_brand and user_data.driver_data.car_brand != user.car_brand:
                    changes.append(("car_brand", user.car_brand, user_data.driver_data.car_brand))
                    user.car_brand = user_data.driver_data.car_brand
                
                if user_data.driver_data.car_model and user_data.driver_data.car_model != user.car_model:
                    changes.append(("car_model", user.car_model, user_data.driver_data.car_model))
                    user.car_model = user_data.driver_data.car_model
                
                if user_data.driver_data.car_year and user_data.driver_data.car_year != user.car_year:
                    # Валидация года автомобиля
                    if user_data.driver_data.car_year < 1900 or user_data.driver_data.car_year > datetime.now().year + 1:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Некорректный год автомобиля"
                        )
                    changes.append(("car_year", str(user.car_year), str(user_data.driver_data.car_year)))
                    user.car_year = user_data.driver_data.car_year
                
                if user_data.driver_data.car_color and user_data.driver_data.car_color != user.car_color:
                    changes.append(("car_color", user.car_color, user_data.driver_data.car_color))
                    user.car_color = user_data.driver_data.car_color
                
                if user_data.driver_data.driver_license_number and user_data.driver_data.driver_license_number != user.driver_license_number:
                    # Валидация номера водительских прав
                    if len(user_data.driver_data.driver_license_number) < 10:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Некорректный номер водительских прав"
                        )
                    changes.append(("driver_license_number", user.driver_license_number, user_data.driver_data.driver_license_number))
                    user.driver_license_number = user_data.driver_data.driver_license_number
                
                if user_data.driver_data.driver_license_photo_url and user_data.driver_data.driver_license_photo_url != user.driver_license_photo_url:
                    # Валидация URL фото прав
                    if not user_data.driver_data.driver_license_photo_url.startswith(('http://', 'https://')):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Некорректный URL фото водительских прав"
                        )
                    changes.append(("driver_license_photo_url", user.driver_license_photo_url, user_data.driver_data.driver_license_photo_url))
                    user.driver_license_photo_url = user_data.driver_data.driver_license_photo_url
                
                if user_data.driver_data.car_photo_url and user_data.driver_data.car_photo_url != user.car_photo_url:
                    # Валидация URL фото автомобиля
                    if not user_data.driver_data.car_photo_url.startswith(('http://', 'https://')):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Некорректный URL фото автомобиля"
                        )
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
                        old_value=str(old_value) if old_value is not None else None,
                        new_value=str(new_value) if new_value is not None else None,
                        changed_by="user"
                    )
                    self.db.add(change_log)
                
                # Обновляем историю в профиле
                if not user.profile_history:
                    user.profile_history = []
                
                for field_name, old_value, new_value in changes:
                    user.profile_history.append({
                        "field_name": field_name,
                        "old_value": str(old_value) if old_value is not None else None,
                        "new_value": str(new_value) if new_value is not None else None,
                        "changed_at": datetime.now().isoformat(),
                        "changed_by": "user"
                    })
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Обновлен профиль пользователя: {user.telegram_id} (ID: {user_id}), изменено полей: {len(changes)}")
            return user
            
        except HTTPException:
            self.db.rollback()
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Ошибка целостности данных при обновлении пользователя {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Конфликт данных при обновлении профиля"
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Ошибка базы данных при обновлении пользователя {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных при обновлении профиля"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Неожиданная ошибка при обновлении пользователя {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка обновления профиля"
            )
    
    def accept_privacy_policy(self, user_id: int, privacy_data: PrivacyPolicyAccept) -> User:
        """Принять пользовательское соглашение с улучшенной обработкой ошибок"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Попытка принятия соглашения несуществующим пользователем: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Валидация данных соглашения
            if not privacy_data.accepted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Необходимо принять пользовательское соглашение"
                )
            
            if not privacy_data.version:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Версия соглашения обязательна"
                )
            
            # Проверяем, не принято ли уже соглашение
            if user.privacy_policy_accepted:
                logger.info(f"Пользователь {user.telegram_id} уже принял соглашение версии {user.privacy_policy_version}")
                return user
            
            user.privacy_policy_accepted = True
            user.privacy_policy_accepted_at = datetime.now()
            user.privacy_policy_version = privacy_data.version
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Пользователь {user.telegram_id} (ID: {user_id}) принял соглашение версии {privacy_data.version}")
            return user
                
        except HTTPException:
            self.db.rollback()
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Ошибка базы данных при принятии соглашения пользователем {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных при принятии соглашения"
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Неожиданная ошибка при принятии соглашения пользователем {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка принятия соглашения"
            )
    
    def verify_telegram_user(self, telegram_data: Dict[str, Any]) -> Optional[User]:
        """Верификация пользователя через Telegram с улучшенной обработкой ошибок"""
        try:
            # Валидация входных данных
            if not telegram_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Отсутствуют данные Telegram"
                )
            
            # Проверяем подпись Telegram
            if not verify_telegram_data(telegram_data):
                logger.warning("Верификация данных Telegram не прошла")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверная подпись Telegram"
                )
            
            # Извлекаем Telegram ID
            user_data = telegram_data.get('user', telegram_data)
            telegram_id = str(user_data.get('id'))
            
            if not telegram_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Отсутствует Telegram ID"
                )
            
            # Ищем пользователя
            user = self.get_user_by_telegram_id(telegram_id)
            if user:
                logger.info(f"Пользователь верифицирован: {telegram_id}")
            else:
                logger.info(f"Пользователь не найден при верификации: {telegram_id}")
            
            return user
            
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Ошибка базы данных при верификации Telegram: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных при верификации"
            )
        except Exception as e:
            logger.error(f"Неожиданная ошибка при верификации Telegram: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка верификации Telegram"
            )
    
    def get_profile_history(self, user_id: int) -> list:
        """Получить историю изменений профиля с улучшенной обработкой ошибок"""
        try:
            # Проверяем существование пользователя
            user = self.get_user_by_id(user_id)
            if not user:
                logger.warning(f"Попытка получения истории несуществующего пользователя: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            logs = self.db.query(ProfileChangeLog).filter(
                ProfileChangeLog.user_id == user_id
            ).order_by(ProfileChangeLog.changed_at.desc()).limit(100).all()
            
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
        except SQLAlchemyError as e:
            logger.error(f"Ошибка базы данных при получении истории профиля {user_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных при получении истории"
            )
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении истории профиля {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка получения истории профиля"
            )
    
    def register(self, user_data):
        """Регистрация пользователя (заглушка для будущей реализации)"""
        logger.warning("Метод register не реализован")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Регистрация через этот метод не поддерживается"
        )

    def login(self, credentials):
        """Авторизация пользователя (заглушка для будущей реализации)"""
        logger.warning("Метод login не реализован")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Авторизация через этот метод не поддерживается"
        )
    
    def update_user_profile(self, user_id: int, profile_data: UserUpdate) -> User:
        """Обновление профиля пользователя (алиас для update_user)"""
        return self.update_user(user_id, profile_data)
    
    def authenticate_user(self, telegram_id: str) -> Dict[str, Any]:
        """
        Аутентификация пользователя через Telegram
        
        Args:
            telegram_id: Telegram ID пользователя
            
        Returns:
            Dict[str, Any]: Данные аутентификации с токенами
        """
        try:
            # Получаем пользователя
            user = self.get_user_by_telegram_id(telegram_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Создаем пару токенов
            tokens = jwt_auth.create_token_pair(user.id, user.telegram_id)
            
            # Обновляем время последнего входа
            user.last_login_at = datetime.now()
            user.updated_at = datetime.now()
            self.db.commit()
            
            logger.info(f"Пользователь {user.telegram_id} успешно аутентифицирован")
            
            return {
                "user": UserRead.from_orm(user),
                "tokens": tokens
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка аутентификации пользователя {telegram_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка аутентификации"
            )
    
    def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """
        Обновление токенов по refresh токену
        
        Args:
            refresh_token: Refresh токен
            
        Returns:
            Dict[str, Any]: Новая пара токенов
        """
        try:
            # Верифицируем refresh токен
            payload = jwt_auth.verify_token(refresh_token, "refresh")
            user_id = payload.get("user_id")
            telegram_id = payload.get("telegram_id")
            
            if not user_id or not telegram_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный refresh токен"
                )
            
            # Проверяем существование пользователя
            user = self.get_user_by_id(user_id)
            if not user or user.telegram_id != telegram_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Пользователь не найден"
                )
            
            # Создаем новую пару токенов
            tokens = jwt_auth.create_token_pair(user.id, user.telegram_id)
            
            logger.info(f"Токены обновлены для пользователя {user_id}")
            
            return {
                "user": UserRead.from_orm(user),
                "tokens": tokens
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка обновления токенов: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ошибка обновления токенов"
            )


# Зависимость для получения текущего пользователя
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя по токену"""
    try:
        # Временная реализация для разработки - возвращаем первого пользователя
        # TODO: Реализовать получение пользователя по JWT токену
        user = db.query(User).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения текущего пользователя: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ошибка авторизации"
        )


