from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from ..database import get_db
from ..services.auth_service import AuthService
from ..schemas.user import UserCreate, UserUpdate, UserRead, PrivacyPolicyAccept
from ..utils.security import verify_telegram_data, extract_telegram_user_data

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post('/telegram/verify')
async def verify_telegram_user(request: Request, db: Session = Depends(get_db)):
    """Верификация пользователя через Telegram Web App"""
    try:
        # Получаем данные из запроса
        telegram_data = await request.json()
        
        logger.info(f"Received Telegram verification request: {telegram_data}")
        
        # Верифицируем данные Telegram
        if not verify_telegram_data(telegram_data):
            logger.warning("Telegram data verification failed")
            # В режиме разработки продолжаем без верификации
            if os.getenv('ENVIRONMENT', 'production') != 'development':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверная подпись Telegram"
                )
        
        # Извлекаем данные пользователя из user объекта
        user_data = extract_telegram_user_data(telegram_data.get('user', telegram_data))
        telegram_id = str(user_data['id'])
        
        # Ищем пользователя в базе
        auth_service = AuthService(db)
        user = auth_service.get_user_by_telegram_id(telegram_id)
        
        if user:
            # Пользователь существует
            return {
                "exists": True,
                "user": UserRead.from_orm(user),
                "telegram_data": user_data
            }
        else:
            # Пользователь не найден, нужно зарегистрироваться
            return {
                "exists": False,
                "telegram_data": user_data
            }
            
    except Exception as e:
        logger.error(f"Ошибка верификации Telegram: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка верификации пользователя"
        )

@router.post('/register')
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    try:
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data)
        
        return {
            "success": True,
            "user": UserRead.from_orm(user),
            "message": "Пользователь успешно зарегистрирован"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка регистрации: {str(e)}")
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
    """Обновление профиля пользователя"""
    try:
        auth_service = AuthService(db)
        user = auth_service.update_user(user_id, user_data)
        
        return {
            "success": True,
            "user": UserRead.from_orm(user),
            "message": "Профиль успешно обновлен"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка обновления профиля: {str(e)}")
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
    """Принятие пользовательского соглашения"""
    try:
        auth_service = AuthService(db)
        user = auth_service.accept_privacy_policy(user_id, privacy_data)
        
        return {
            "success": True,
            "user": UserRead.from_orm(user),
            "message": "Пользовательское соглашение принято"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка принятия соглашения: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка принятия соглашения"
        )

@router.get('/profile/{user_id}')
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Получение профиля пользователя"""
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        return UserRead.from_orm(user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения профиля: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения профиля"
        )

@router.get('/profile/{user_id}/history')
async def get_profile_history(user_id: int, db: Session = Depends(get_db)):
    """Получение истории изменений профиля"""
    try:
        auth_service = AuthService(db)
        history = auth_service.get_profile_history(user_id)
        
        return {
            "user_id": user_id,
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения истории профиля: {str(e)}")
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
        3.2. Пользователь дает согласие на обработку своих персональных данных.
        
        4. ОТВЕТСТВЕННОСТЬ
        4.1. Сервис не несет ответственности за действия пользователей.
        4.2. Пользователь несет полную ответственность за свои действия.
        
        5. ИЗМЕНЕНИЯ В СОГЛАШЕНИИ
        5.1. Сервис оставляет за собой право изменять настоящее Соглашение.
        5.2. Изменения вступают в силу с момента их публикации.
        
        Версия: 1.1
        Дата вступления в силу: 01.01.2024
        """
    } 