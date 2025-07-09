from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime

from ..database import get_db
from ..services.auth_service import AuthService
from ..utils.jwt_auth import get_current_user, require_auth
from ..schemas.user import UserRead, UserUpdate, DriverData
from ..models.user import User
from ..utils.error_handler import ErrorHandler
from ..utils.logger import get_logger

logger = get_logger("profile_api")
router = APIRouter()

@router.get('/', response_model=UserRead)
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Получение профиля текущего пользователя
    
    Returns:
        UserRead: Данные профиля пользователя
    """
    try:
        logger.info(f"Получение профиля пользователя {current_user.id}")
        
        # Обновляем время последнего доступа
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        return UserRead.from_orm(current_user)
        
    except Exception as e:
        logger.error(f"Ошибка получения профиля пользователя {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения профиля"
        )

@router.put('/', response_model=UserRead)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Обновление профиля пользователя
    
    Args:
        profile_data: Данные для обновления профиля
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        UserRead: Обновленные данные профиля
    """
    try:
        logger.info(f"Обновление профиля пользователя {current_user.id}")
        
        auth_service = AuthService(db)
        updated_user = auth_service.update_user_profile(current_user.id, profile_data)
        
        logger.info(f"Профиль пользователя {current_user.id} успешно обновлен")
        return UserRead.from_orm(updated_user)
        
    except ValueError as e:
        logger.warning(f"Ошибка валидации при обновлении профиля {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Ошибка обновления профиля пользователя {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления профиля"
        )

@router.post('/avatar')
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Загрузка аватара пользователя
    
    Args:
        file: Файл изображения
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        dict: Результат загрузки
    """
    try:
        logger.info(f"Загрузка аватара пользователя {current_user.id}")
        
        # Валидация файла
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть изображением"
            )
        
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Размер файла не должен превышать 10MB"
            )
        
        # Здесь должна быть логика сохранения файла
        # Пока возвращаем заглушку
        avatar_url = f"/uploads/avatars/{current_user.id}_{datetime.utcnow().timestamp()}.jpg"
        
        # Обновляем профиль пользователя
        current_user.avatar_url = avatar_url
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Аватар пользователя {current_user.id} успешно загружен")
        return {
            "success": True,
            "avatar_url": avatar_url,
            "message": "Аватар успешно загружен"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки аватара пользователя {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка загрузки аватара"
        )

@router.post('/driver-license')
async def upload_driver_license(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Загрузка фото водительских прав
    
    Args:
        file: Файл изображения
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        dict: Результат загрузки
    """
    try:
        logger.info(f"Загрузка водительских прав пользователя {current_user.id}")
        
        # Валидация файла
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть изображением"
            )
        
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Размер файла не должен превышать 10MB"
            )
        
        # Здесь должна быть логика сохранения файла
        license_url = f"/uploads/licenses/{current_user.id}_{datetime.utcnow().timestamp()}.jpg"
        
        # Обновляем профиль пользователя
        current_user.driver_license_photo_url = license_url
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Водительские права пользователя {current_user.id} успешно загружены")
        return {
            "success": True,
            "license_url": license_url,
            "message": "Фото водительских прав успешно загружено"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки водительских прав пользователя {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка загрузки водительских прав"
        )

@router.post('/car-photo')
async def upload_car_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Загрузка фото автомобиля
    
    Args:
        file: Файл изображения
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        dict: Результат загрузки
    """
    try:
        logger.info(f"Загрузка фото автомобиля пользователя {current_user.id}")
        
        # Валидация файла
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть изображением"
            )
        
        if file.size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Размер файла не должен превышать 10MB"
            )
        
        # Здесь должна быть логика сохранения файла
        car_photo_url = f"/uploads/cars/{current_user.id}_{datetime.utcnow().timestamp()}.jpg"
        
        # Обновляем профиль пользователя
        current_user.car_photo_url = car_photo_url
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Фото автомобиля пользователя {current_user.id} успешно загружено")
        return {
            "success": True,
            "car_photo_url": car_photo_url,
            "message": "Фото автомобиля успешно загружено"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки фото автомобиля пользователя {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка загрузки фото автомобиля"
        )

@router.get('/statistics')
async def get_profile_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение статистики профиля пользователя
    
    Args:
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        dict: Статистика профиля
    """
    try:
        logger.info(f"Получение статистики профиля пользователя {current_user.id}")
        
        # Здесь должна быть логика получения статистики
        # Пока возвращаем базовую информацию
        statistics = {
            "total_rides": current_user.total_rides or 0,
            "average_rating": current_user.average_rating or 0.0,
            "cancelled_rides": current_user.cancelled_rides or 0,
            "is_driver": current_user.is_driver,
            "is_verified": current_user.is_verified,
            "member_since": current_user.created_at.isoformat() if current_user.created_at else None,
            "last_active": current_user.updated_at.isoformat() if current_user.updated_at else None
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики профиля пользователя {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения статистики профиля"
        ) 