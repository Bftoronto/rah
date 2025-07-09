from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path

from ..database import get_db
from ..utils.jwt_auth import get_current_user
from ..models.user import User
from ..schemas.upload import UploadResponse
from ..utils.logger import get_logger
from ..config.settings import settings

logger = get_logger("upload_api")
router = APIRouter()

# Создаем директории для загрузки, если их нет
def ensure_upload_dirs():
    """Создание директорий для загрузки файлов"""
    upload_dirs = [
        settings.upload_dir,
        f"{settings.upload_dir}/avatars",
        f"{settings.upload_dir}/licenses", 
        f"{settings.upload_dir}/cars",
        f"{settings.upload_dir}/temp"
    ]
    
    for dir_path in upload_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

# Валидация файла
def validate_file(file: UploadFile, max_size: int = 10 * 1024 * 1024) -> None:
    """
    Валидация загружаемого файла
    
    Args:
        file: Загружаемый файл
        max_size: Максимальный размер файла в байтах
    
    Raises:
        HTTPException: При ошибке валидации
    """
    # Проверка типа файла
    allowed_types = [
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
        'application/pdf', 'image/webp'
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неподдерживаемый тип файла: {file.content_type}. Разрешены: {', '.join(allowed_types)}"
        )
    
    # Проверка размера файла
    if hasattr(file, 'size') and file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Размер файла превышает максимально допустимый: {max_size / (1024 * 1024)}MB"
        )

# Сохранение файла
def save_file(file: UploadFile, directory: str, filename: str) -> str:
    """
    Сохранение файла на диск
    
    Args:
        file: Загружаемый файл
        directory: Директория для сохранения
        filename: Имя файла
    
    Returns:
        str: Путь к сохраненному файлу
    """
    try:
        # Создаем директории если их нет
        ensure_upload_dirs()
        
        # Формируем полный путь
        file_path = os.path.join(directory, filename)
        
        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        # Возвращаем относительный путь для URL
        relative_path = os.path.relpath(file_path, settings.upload_dir)
        return f"/uploads/{relative_path}"
        
    except Exception as e:
        logger.error(f"Ошибка сохранения файла {filename}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сохранения файла"
        )

@router.post('/', response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(..., description="Тип файла: avatar, license, car"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Универсальная загрузка файлов
    
    Args:
        file: Загружаемый файл
        file_type: Тип файла (avatar, license, car)
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        UploadResponse: Результат загрузки
    """
    try:
        logger.info(f"Загрузка файла типа {file_type} пользователем {current_user.id}")
        
        # Валидация типа файла
        allowed_types = ['avatar', 'license', 'car']
        if file_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый тип файла: {file_type}. Разрешены: {', '.join(allowed_types)}"
            )
        
        # Валидация файла
        validate_file(file)
        
        # Генерируем уникальное имя файла
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"{current_user.id}_{uuid.uuid4().hex}{file_extension}"
        
        # Определяем директорию для сохранения
        upload_dirs = {
            'avatar': f"{settings.upload_dir}/avatars",
            'license': f"{settings.upload_dir}/licenses", 
            'car': f"{settings.upload_dir}/cars"
        }
        
        directory = upload_dirs[file_type]
        
        # Сохраняем файл
        file_url = save_file(file, directory, unique_filename)
        
        # Обновляем профиль пользователя
        if file_type == 'avatar':
            current_user.avatar_url = file_url
        elif file_type == 'license':
            current_user.driver_license_photo_url = file_url
        elif file_type == 'car':
            current_user.car_photo_url = file_url
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Файл {file_type} успешно загружен пользователем {current_user.id}: {file_url}")
        
        return UploadResponse(
            success=True,
            file_url=file_url,
            file_type=file_type,
            original_filename=file.filename,
            file_size=len(file.file.read()) if hasattr(file.file, 'read') else 0,
            message=f"Файл {file_type} успешно загружен"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки файла {file_type} пользователем {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка загрузки файла"
        )

@router.post('/avatar', response_model=UploadResponse)
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
        UploadResponse: Результат загрузки
    """
    try:
        logger.info(f"Загрузка аватара пользователем {current_user.id}")
        
        # Валидация файла
        validate_file(file, max_size=5 * 1024 * 1024)  # 5MB для аватара
        
        # Проверяем, что это изображение
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть изображением"
            )
        
        # Генерируем уникальное имя файла
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"avatar_{current_user.id}_{uuid.uuid4().hex}{file_extension}"
        
        # Сохраняем файл
        directory = f"{settings.upload_dir}/avatars"
        file_url = save_file(file, directory, unique_filename)
        
        # Обновляем профиль пользователя
        current_user.avatar_url = file_url
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Аватар успешно загружен пользователем {current_user.id}: {file_url}")
        
        return UploadResponse(
            success=True,
            file_url=file_url,
            file_type="avatar",
            original_filename=file.filename,
            file_size=len(file.file.read()) if hasattr(file.file, 'read') else 0,
            message="Аватар успешно загружен"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки аватара пользователем {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка загрузки аватара"
        )

@router.post('/driver-license', response_model=UploadResponse)
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
        UploadResponse: Результат загрузки
    """
    try:
        logger.info(f"Загрузка водительских прав пользователем {current_user.id}")
        
        # Валидация файла
        validate_file(file, max_size=10 * 1024 * 1024)  # 10MB для документов
        
        # Проверяем, что это изображение или PDF
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть изображением или PDF"
            )
        
        # Генерируем уникальное имя файла
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"license_{current_user.id}_{uuid.uuid4().hex}{file_extension}"
        
        # Сохраняем файл
        directory = f"{settings.upload_dir}/licenses"
        file_url = save_file(file, directory, unique_filename)
        
        # Обновляем профиль пользователя
        current_user.driver_license_photo_url = file_url
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Водительские права успешно загружены пользователем {current_user.id}: {file_url}")
        
        return UploadResponse(
            success=True,
            file_url=file_url,
            file_type="license",
            original_filename=file.filename,
            file_size=len(file.file.read()) if hasattr(file.file, 'read') else 0,
            message="Фото водительских прав успешно загружено"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки водительских прав пользователем {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка загрузки водительских прав"
        )

@router.post('/car-photo', response_model=UploadResponse)
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
        UploadResponse: Результат загрузки
    """
    try:
        logger.info(f"Загрузка фото автомобиля пользователем {current_user.id}")
        
        # Валидация файла
        validate_file(file, max_size=10 * 1024 * 1024)  # 10MB для фото
        
        # Проверяем, что это изображение
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть изображением"
            )
        
        # Генерируем уникальное имя файла
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"car_{current_user.id}_{uuid.uuid4().hex}{file_extension}"
        
        # Сохраняем файл
        directory = f"{settings.upload_dir}/cars"
        file_url = save_file(file, directory, unique_filename)
        
        # Обновляем профиль пользователя
        current_user.car_photo_url = file_url
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Фото автомобиля успешно загружено пользователем {current_user.id}: {file_url}")
        
        return UploadResponse(
            success=True,
            file_url=file_url,
            file_type="car",
            original_filename=file.filename,
            file_size=len(file.file.read()) if hasattr(file.file, 'read') else 0,
            message="Фото автомобиля успешно загружено"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка загрузки фото автомобиля пользователем {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка загрузки фото автомобиля"
        )

@router.delete('/{file_type}/{filename}')
async def delete_file(
    file_type: str,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление загруженного файла
    
    Args:
        file_type: Тип файла (avatar, license, car)
        filename: Имя файла
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        dict: Результат удаления
    """
    try:
        logger.info(f"Удаление файла {file_type}/{filename} пользователем {current_user.id}")
        
        # Валидация типа файла
        allowed_types = ['avatar', 'license', 'car']
        if file_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый тип файла: {file_type}"
            )
        
        # Формируем путь к файлу
        file_path = os.path.join(settings.upload_dir, file_type, filename)
        
        # Проверяем существование файла
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Файл не найден"
            )
        
        # Удаляем файл
        os.remove(file_path)
        
        # Обновляем профиль пользователя
        if file_type == 'avatar':
            current_user.avatar_url = None
        elif file_type == 'license':
            current_user.driver_license_photo_url = None
        elif file_type == 'car':
            current_user.car_photo_url = None
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Файл {file_type}/{filename} успешно удален пользователем {current_user.id}")
        
        return {
            "success": True,
            "message": f"Файл {file_type} успешно удален"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления файла {file_type}/{filename} пользователем {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка удаления файла"
        ) 