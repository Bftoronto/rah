from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
import os
import uuid
from pydantic import ValidationError

from ..database import get_db
from ..services.auth_service import AuthService
from ..schemas.user import UserCreate, UserUpdate, UserRead, PrivacyPolicyAccept
from ..models.user import User
from ..schemas.telegram import TelegramWebAppData, TelegramVerificationRequest, TelegramAuthRequest, TelegramRefreshRequest, TelegramUserData
from ..utils.security import verify_telegram_data, extract_telegram_user_data
from ..utils.jwt_auth import get_current_user_optional, require_auth, require_driver, require_verified_user
from ..schemas.responses import create_success_response, create_error_response, create_validation_error_response
from ..utils.logger import get_logger

logger = get_logger("auth_api")
router = APIRouter()

@router.post('/telegram/verify', response_model=dict)
async def verify_telegram_user(request: Request, db: Session = Depends(get_db)):
    """Верификация пользователя через Telegram с унифицированной структурой данных"""
    try:
        raw_data = await request.json()
        logger.info(f"Получены данные Telegram: {raw_data}")
        
        # Унифицированная обработка данных от фронтенда
        user_data = None
        telegram_data = None
        
        # Проверяем структуру данных от фронтенда
        if 'user' in raw_data and isinstance(raw_data['user'], dict):
            # Структура от фронтенда: {user: {...}, auth_date: ..., hash: ...}
            try:
                auth_request = TelegramAuthRequest(**raw_data)
                telegram_data = auth_request.dict()
                user_data = auth_request.user.dict()
            except ValidationError as e:
                logger.error(f"Ошибка валидации TelegramAuthRequest: {e}")
                return create_validation_error_response(
                    field_errors={'telegram_data': [f"Некорректная структура данных: {str(e)}"]},
                    message="Ошибка валидации данных Telegram",
                    request_id=str(uuid.uuid4())
                )
        else:
            # Старая структура или прямая структура пользователя
            try:
                # Пытаемся обработать как прямые данные пользователя
                user_data = TelegramUserData(**raw_data).dict()
                telegram_data = {
                    'user': user_data,
                    'auth_date': raw_data.get('auth_date'),
                    'hash': raw_data.get('hash')
                }
            except ValidationError:
                try:
                    # Пытаемся обработать как WebApp данные
                    webapp_data = TelegramWebAppData(**raw_data)
                    telegram_data = webapp_data.dict()
                    user_data = webapp_data.user.dict()
                except ValidationError as e:
                    logger.error(f"Ошибка валидации всех форматов Telegram данных: {e}")
                    return create_validation_error_response(
                        field_errors={'telegram_data': [f"Некорректные данные Telegram: {str(e)}"]},
                        message="Ошибка валидации данных Telegram",
                        request_id=str(uuid.uuid4())
                    )
        
        # Извлекаем Telegram ID
        telegram_id = str(user_data.get('id'))
        if not telegram_id:
            return create_error_response(
                message="Отсутствует Telegram ID",
                error_code="MISSING_TELEGRAM_ID",
                request_id=str(uuid.uuid4())
            )
        
        logger.info(f"Получен запрос верификации Telegram для пользователя: {telegram_id}")
        
        # Верифицируем данные Telegram (в режиме разработки пропускаем)
        if os.getenv('ENVIRONMENT', 'production') == 'development':
            logger.info("Режим разработки: пропускаем верификацию подписи Telegram")
        else:
            if not verify_telegram_data(telegram_data):
                logger.warning(f"Верификация данных Telegram не прошла для пользователя: {telegram_id}")
                return create_error_response(
                    message="Неверная подпись Telegram",
                    error_code="INVALID_TELEGRAM_SIGNATURE",
                    request_id=str(uuid.uuid4())
                )
        
        # Ищем пользователя в базе
        auth_service = AuthService(db)
        user = auth_service.get_user_by_telegram_id(telegram_id)
        
        if user:
            # Пользователь существует
            logger.info(f"Пользователь найден: {telegram_id}")
            return create_success_response(
                data={
                    "exists": True,
                    "user": UserRead.from_orm(user).dict(),
                    "telegram_data": user_data
                },
                message="Пользователь найден",
                request_id=str(uuid.uuid4())
            )
        else:
            # Пользователь не найден, нужно зарегистрироваться
            logger.info(f"Пользователь не найден, требуется регистрация: {telegram_id}")
            return create_success_response(
                data={
                    "exists": False,
                    "telegram_data": user_data
                },
                message="Пользователь не найден, требуется регистрация",
                request_id=str(uuid.uuid4())
            )
            
    except Exception as e:
        logger.error(f"Критическая ошибка верификации Telegram: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка верификации пользователя",
            error_code="VERIFICATION_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.post('/register', response_model=dict)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя с валидацией"""
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        
        logger.info(f"Пользователь успешно зарегистрирован: {user.telegram_id}")
        return create_success_response(
            data={
                "user": UserRead.from_orm(user).dict()
            },
            message="Пользователь успешно зарегистрирован",
            request_id=str(uuid.uuid4())
        )
        
    except ValidationError as e:
        logger.error(f"Ошибка валидации при регистрации: {str(e)}")
        return create_validation_error_response(
            field_errors={'user_data': [f"Некорректные данные регистрации: {str(e)}"]},
            message="Ошибка валидации данных регистрации",
            request_id=str(uuid.uuid4())
        )
    except Exception as e:
        logger.error(f"Критическая ошибка регистрации: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка регистрации пользователя",
            error_code="REGISTRATION_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.put('/profile/{user_id}', response_model=dict)
async def update_profile(
    user_id: int, 
    user_data: UserUpdate, 
    db: Session = Depends(get_db)
):
    """Обновление профиля пользователя с валидацией"""
    try:
        auth_service = AuthService(db)
        user = auth_service.update_user(user_id, user_data)
        
        logger.info(f"Профиль пользователя обновлен: {user_id}")
        return create_success_response(
            data={
                "user": UserRead.from_orm(user).dict()
            },
            message="Профиль успешно обновлен",
            request_id=str(uuid.uuid4())
        )
        
    except ValidationError as e:
        logger.error(f"Ошибка валидации при обновлении профиля: {str(e)}")
        return create_validation_error_response(
            field_errors={'user_data': [f"Некорректные данные профиля: {str(e)}"]},
            message="Ошибка валидации данных профиля",
            request_id=str(uuid.uuid4())
        )
    except Exception as e:
        logger.error(f"Критическая ошибка обновления профиля: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка обновления профиля",
            error_code="PROFILE_UPDATE_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.post('/privacy-policy/accept/{user_id}', response_model=dict)
async def accept_privacy_policy(
    user_id: int,
    privacy_data: PrivacyPolicyAccept,
    db: Session = Depends(get_db)
):
    """Принятие пользовательского соглашения с валидацией"""
    try:
        auth_service = AuthService(db)
        user = auth_service.accept_privacy_policy(user_id, privacy_data)
        
        logger.info(f"Пользовательское соглашение принято: {user_id}")
        return create_success_response(
            data={
                "user": UserRead.from_orm(user).dict()
            },
            message="Пользовательское соглашение принято",
            request_id=str(uuid.uuid4())
        )
        
    except ValidationError as e:
        logger.error(f"Ошибка валидации при принятии соглашения: {str(e)}")
        return create_validation_error_response(
            field_errors={'privacy_data': [f"Некорректные данные соглашения: {str(e)}"]},
            message="Ошибка валидации данных соглашения",
            request_id=str(uuid.uuid4())
        )
    except Exception as e:
        logger.error(f"Критическая ошибка принятия соглашения: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка принятия соглашения",
            error_code="PRIVACY_ACCEPT_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.get('/profile/{user_id}', response_model=dict)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Получение профиля пользователя"""
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            return create_error_response(
                message="Пользователь не найден",
                error_code="USER_NOT_FOUND",
                request_id=str(uuid.uuid4())
            )
        
        logger.info(f"Профиль пользователя получен: {user_id}")
        return create_success_response(
            data={
                "user": UserRead.from_orm(user).dict()
            },
            message="Профиль пользователя получен",
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения профиля пользователя: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка получения профиля пользователя",
            error_code="PROFILE_GET_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.get('/profile/{user_id}/history', response_model=dict)
async def get_profile_history(user_id: int, db: Session = Depends(get_db)):
    """Получение истории пользователя"""
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            return create_error_response(
                message="Пользователь не найден",
                error_code="USER_NOT_FOUND",
                request_id=str(uuid.uuid4())
            )
        
        # Здесь можно добавить логику получения истории
        history = {
            "rides": [],
            "ratings": [],
            "reviews": []
        }
        
        logger.info(f"История пользователя получена: {user_id}")
        return create_success_response(
            data={
                "user_id": user_id,
                "history": history
            },
            message="История пользователя получена",
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения истории пользователя: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка получения истории пользователя",
            error_code="HISTORY_GET_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.get('/privacy-policy', response_model=dict)
async def get_privacy_policy():
    """Получение текста пользовательского соглашения"""
    try:
        privacy_policy = {
            "title": "Пользовательское соглашение",
            "content": "Текст пользовательского соглашения...",
            "version": "1.0",
            "last_updated": "2024-01-01"
        }
        
        return create_success_response(
            data=privacy_policy,
            message="Пользовательское соглашение получено",
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения пользовательского соглашения: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка получения пользовательского соглашения",
            error_code="PRIVACY_GET_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.post('/login', response_model=dict)
async def login_user(telegram_data: TelegramAuthRequest, db: Session = Depends(get_db)):
    """Вход пользователя через Telegram"""
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_telegram_id(str(telegram_data.user.id))
        
        if not user:
            return create_error_response(
                message="Пользователь не найден",
                error_code="USER_NOT_FOUND",
                request_id=str(uuid.uuid4())
            )
        
        # Генерируем токены
        access_token = auth_service.create_access_token(user.id)
        refresh_token = auth_service.create_refresh_token(user.id)
        
        logger.info(f"Пользователь успешно вошел: {user.telegram_id}")
        return create_success_response(
            data={
                "user": UserRead.from_orm(user).dict(),
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            message="Вход выполнен успешно",
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Ошибка входа пользователя: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка входа пользователя",
            error_code="LOGIN_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.post('/refresh', response_model=dict)
async def refresh_tokens(
    refresh_data: TelegramRefreshRequest, 
    db: Session = Depends(get_db)
):
    """Обновление токенов доступа"""
    try:
        auth_service = AuthService(db)
        user_id = auth_service.verify_refresh_token(refresh_data.refresh_token)
        
        if not user_id:
            return create_error_response(
                message="Недействительный refresh токен",
                error_code="INVALID_REFRESH_TOKEN",
                request_id=str(uuid.uuid4())
            )
        
        # Генерируем новые токены
        access_token = auth_service.create_access_token(user_id)
        refresh_token = auth_service.create_refresh_token(user_id)
        
        logger.info(f"Токены обновлены для пользователя: {user_id}")
        return create_success_response(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token
            },
            message="Токены обновлены",
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Ошибка обновления токенов: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка обновления токенов",
            error_code="REFRESH_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.post('/logout', response_model=dict)
async def logout_user(current_user: User = Depends(require_auth)):
    """Выход пользователя"""
    try:
        # В реальном приложении здесь можно добавить логику инвалидации токенов
        logger.info(f"Пользователь вышел: {current_user.telegram_id}")
        return create_success_response(
            message="Выход выполнен успешно",
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Ошибка выхода пользователя: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка выхода пользователя",
            error_code="LOGOUT_ERROR",
            request_id=str(uuid.uuid4())
        )

@router.get('/me', response_model=dict)
async def get_current_user_info(current_user: User = Depends(require_auth)):
    """Получение информации о текущем пользователе"""
    try:
        logger.info(f"Информация о текущем пользователе получена: {current_user.telegram_id}")
        return create_success_response(
            data={
                "user": UserRead.from_orm(current_user).dict()
            },
            message="Информация о пользователе получена",
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения информации о пользователе: {str(e)}", exc_info=True)
        return create_error_response(
            message="Ошибка получения информации о пользователе",
            error_code="ME_GET_ERROR",
            request_id=str(uuid.uuid4())
        ) 