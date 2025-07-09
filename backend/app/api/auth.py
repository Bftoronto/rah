from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
import os
from pydantic import ValidationError

from ..database import get_db
from ..services.auth_service import AuthService
from ..schemas.user import UserCreate, UserUpdate, UserRead, PrivacyPolicyAccept
from ..models.user import User
from ..schemas.telegram import TelegramWebAppData, TelegramVerificationRequest, TelegramAuthRequest, TelegramRefreshRequest
from ..utils.security import verify_telegram_data, extract_telegram_user_data
from ..utils.jwt_auth import get_current_user_optional, require_auth, require_driver, require_verified_user

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post('/telegram/verify')
async def verify_telegram_user(request: Request, db: Session = Depends(get_db)):
    """Верификация пользователя через Telegram Web App с поддержкой разных форматов данных"""
    try:
        # Получаем и валидируем данные из запроса
        raw_data = await request.json()
        
        # Пытаемся валидировать через разные схемы
        telegram_data = None
        user_data = None
        
        # Сначала пробуем новую схему для совместимости с фронтендом
        try:
            auth_request = TelegramAuthRequest(**raw_data)
            telegram_data = auth_request.dict()
            user_data = auth_request.user.dict()
            logger.info(f"Использована схема TelegramAuthRequest для пользователя: {auth_request.user.id}")
        except ValidationError:
            # Если не подходит, пробуем старую схему
            try:
                webapp_data = TelegramWebAppData(**raw_data)
                telegram_data = webapp_data.dict()
                user_data = webapp_data.user.dict()
                logger.info(f"Использована схема TelegramWebAppData для пользователя: {webapp_data.user.id}")
            except ValidationError as e:
                logger.warning(f"Валидация данных Telegram не прошла: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Некорректные данные Telegram: {str(e)}"
                )
        
        # Извлекаем Telegram ID
        telegram_id = str(user_data.get('id'))
        if not telegram_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Отсутствует Telegram ID"
            )
        
        logger.info(f"Получен запрос верификации Telegram для пользователя: {telegram_id}")
        
        # Верифицируем данные Telegram (в режиме разработки пропускаем)
        if os.getenv('ENVIRONMENT', 'production') == 'development':
            logger.info("Режим разработки: пропускаем верификацию подписи Telegram")
        else:
            if not verify_telegram_data(telegram_data):
                logger.warning(f"Верификация данных Telegram не прошла для пользователя: {telegram_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверная подпись Telegram"
                )
        
        # Ищем пользователя в базе
        auth_service = AuthService(db)
        user = auth_service.get_user_by_telegram_id(telegram_id)
        
        if user:
            # Пользователь существует
            logger.info(f"Пользователь найден: {telegram_id}")
            return {
                "exists": True,
                "user": UserRead.from_orm(user),
                "telegram_data": user_data
            }
        else:
            # Пользователь не найден, нужно зарегистрироваться
            logger.info(f"Пользователь не найден, требуется регистрация: {telegram_id}")
            return {
                "exists": False,
                "telegram_data": user_data
            }
            
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"Ошибка валидации данных: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные данные: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Критическая ошибка верификации Telegram: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка верификации пользователя"
        )

@router.post('/register')
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя с валидацией"""
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        
        logger.info(f"Пользователь успешно зарегистрирован: {user.telegram_id}")
        return {
            "success": True,
            "user": UserRead.from_orm(user),
            "message": "Пользователь успешно зарегистрирован"
        }
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"Ошибка валидации при регистрации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные данные регистрации: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Критическая ошибка регистрации: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка регистрации пользователя"
        )

@router.put('/profile/{user_id}')
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
        return {
            "success": True,
            "user": UserRead.from_orm(user),
            "message": "Профиль успешно обновлен"
        }
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"Ошибка валидации при обновлении профиля: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные данные профиля: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Критическая ошибка обновления профиля: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления профиля"
        )

@router.post('/privacy-policy/accept/{user_id}')
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
        return {
            "success": True,
            "user": UserRead.from_orm(user),
            "message": "Пользовательское соглашение принято"
        }
        
    except HTTPException:
        raise
    except ValidationError as e:
        logger.error(f"Ошибка валидации при принятии соглашения: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные данные соглашения: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Критическая ошибка принятия соглашения: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка принятия соглашения"
        )

@router.get('/profile/{user_id}')
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Получение профиля пользователя с валидацией ID"""
    try:
        # Валидация user_id
        if user_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный ID пользователя"
            )
        
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            logger.warning(f"Пользователь не найден: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        logger.info(f"Профиль пользователя получен: {user_id}")
        return UserRead.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Критическая ошибка получения профиля: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения профиля"
        )

@router.get('/profile/{user_id}/history')
async def get_profile_history(user_id: int, db: Session = Depends(get_db)):
    """Получение истории изменений профиля с валидацией"""
    try:
        # Валидация user_id
        if user_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный ID пользователя"
            )
        
        auth_service = AuthService(db)
        history = auth_service.get_profile_history(user_id)
        
        logger.info(f"История профиля получена: {user_id}")
        return {
            "user_id": user_id,
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Критическая ошибка получения истории профиля: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения истории профиля"
        )

@router.get('/privacy-policy')
async def get_privacy_policy():
    """Получение текста пользовательского соглашения"""
    return {
        "version": "1.1",
        "title": "Пользовательское соглашение",
        "content": """
        Настоящее Пользовательское соглашение (далее — Соглашение) регулирует отношения между пользователем и сервисом поиска попутчиков.
        
        1. ОБЩИЕ ПОЛОЖЕНИЯ
        1.1. Использование сервиса означает полное и безоговорочное принятие настоящего Соглашения.
        1.2. Сервис предоставляет платформу для поиска попутчиков и организации совместных поездок.
        
        2. ПРАВА И ОБЯЗАННОСТИ ПОЛЬЗОВАТЕЛЯ
        2.1. Пользователь обязуется предоставлять достоверную информацию при регистрации.
        2.2. Пользователь несет ответственность за безопасность своих поездок.
        2.3. Запрещается использовать сервис для незаконной деятельности.
        
        3. ОБРАБОТКА ПЕРСОНАЛЬНЫХ ДАННЫХ
        3.1. Сервис обрабатывает персональные данные в соответствии с законодательством РФ.
        """
    }

@router.post('/login')
async def login_user(telegram_data: TelegramAuthRequest, db: Session = Depends(get_db)):
    """Аутентификация пользователя через Telegram с выдачей JWT токенов"""
    try:
        auth_service = AuthService(db)
        
        # Извлекаем Telegram ID
        telegram_id = str(telegram_data.user.id)
        
        # Аутентифицируем пользователя
        auth_result = auth_service.authenticate_user(telegram_id)
        
        logger.info(f"Пользователь успешно аутентифицирован: {telegram_id}")
        return {
            "success": True,
            "message": "Успешная аутентификация",
            **auth_result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка аутентификации: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка аутентификации"
        )

@router.post('/refresh')
async def refresh_tokens(
    refresh_data: TelegramRefreshRequest, 
    db: Session = Depends(get_db)
):
    """Обновление JWT токенов"""
    try:
        auth_service = AuthService(db)
        tokens = auth_service.refresh_tokens(refresh_data.refresh_token)
        
        logger.info(f"Токены успешно обновлены")
        return {
            "success": True,
            "tokens": tokens,
            "message": "Токены успешно обновлены"
        }
        
    except ValueError as e:
        logger.warning(f"Ошибка обновления токенов: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный refresh токен"
        )
    except Exception as e:
        logger.error(f"Критическая ошибка обновления токенов: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления токенов"
        )

@router.post('/logout')
async def logout_user(current_user: User = Depends(require_auth)):
    """Выход пользователя из системы"""
    try:
        # В реальной системе здесь можно добавить токен в черный список
        logger.info(f"Пользователь {current_user.telegram_id} вышел из системы")
        
        return {
            "success": True,
            "message": "Успешный выход из системы"
        }
        
    except Exception as e:
        logger.error(f"Ошибка выхода из системы: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка выхода из системы"
        )

@router.get('/me')
async def get_current_user_info(current_user: User = Depends(require_auth)):
    """Получение информации о текущем пользователе"""
    try:
        return {
            "success": True,
            "user": UserRead.from_orm(current_user)
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения информации о пользователе: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения информации о пользователе"
        ) 