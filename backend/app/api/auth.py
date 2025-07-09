from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging
import os
from pydantic import ValidationError

from ..database import get_db
from ..services.auth_service import AuthService
from ..schemas.user import UserCreate, UserUpdate, UserRead, PrivacyPolicyAccept
from ..schemas.telegram import TelegramWebAppData, TelegramVerificationRequest
from ..utils.security import verify_telegram_data, extract_telegram_user_data

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post('/telegram/verify')
async def verify_telegram_user(request: Request, db: Session = Depends(get_db)):
    """Верификация пользователя через Telegram Web App с строгой валидацией"""
    try:
        # Получаем и валидируем данные из запроса
        raw_data = await request.json()
        
        # Строгая валидация через Pydantic
        try:
            telegram_data = TelegramWebAppData(**raw_data)
        except ValidationError as e:
            logger.warning(f"Валидация данных Telegram не прошла: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Некорректные данные Telegram: {str(e)}"
            )
        
        logger.info(f"Получен запрос верификации Telegram для пользователя: {telegram_data.user.id}")
        
        # Верифицируем данные Telegram
        if not verify_telegram_data(telegram_data.dict()):
            logger.warning(f"Верификация данных Telegram не прошла для пользователя: {telegram_data.user.id}")
            # В режиме разработки продолжаем без верификации
            if os.getenv('ENVIRONMENT', 'production') != 'development':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверная подпись Telegram"
                )
        
        # Извлекаем данные пользователя
        user_data = extract_telegram_user_data(telegram_data.user.dict())
        telegram_id = str(user_data['id'])
        
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