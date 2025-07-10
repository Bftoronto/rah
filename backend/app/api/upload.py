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
from ..schemas.responses import create_success_response, create_error_response, create_validation_error_response
from ..utils.logger import get_logger
from ..utils.file_handler import get_file_handler, FileValidationError, FileProcessingError
from ..config.settings import settings

logger = get_logger("upload_api")
router = APIRouter()

# Получаем обработчик файлов
file_handler = get_file_handler(settings.upload_dir)

@router.post('/', response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form(..., description="Тип файла: avatar, license, car, document"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Универсальная загрузка файлов с улучшенной обработкой ошибок
    
    Args:
        file: Загружаемый файл
        file_type: Тип файла (avatar, license, car, document)
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        logger.info(f"Загрузка файла типа {file_type} пользователем {current_user.id}")
        
        # Читаем данные файла
        file_data = await file.read()
        
        # Обрабатываем файл
        result = file_handler.process_file(file_data, file.filename, file_type, current_user.id)
        
        # Обновляем профиль пользователя
        if file_type == 'avatar':
            current_user.avatar_url = result['file_url']
        elif file_type == 'license':
            current_user.driver_license_photo_url = result['file_url']
        elif file_type == 'car':
            current_user.car_photo_url = result['file_url']
        
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Файл {file_type} успешно загружен пользователем {current_user.id}: {result['file_url']}")
        
        return create_success_response(
            data={
                'file_url': result['file_url'],
                'file_type': result['file_type'],
                'original_filename': result['original_filename'],
                'file_size': result['file_size'],
                'file_hash': result['file_hash'],
                'mime_type': result['mime_type']
            },
            message=f"Файл {file_type} успешно загружен"
        )
        
    except FileValidationError as e:
        logger.warning(f"Ошибка валидации файла {file_type} пользователем {current_user.id}: {e.message}")
        return create_validation_error_response(
            field_errors={'file': [e.message]},
            message="Ошибка валидации файла",
            request_id=str(uuid.uuid4())
        )
        
    except FileProcessingError as e:
        logger.error(f"Ошибка обработки файла {file_type} пользователем {current_user.id}: {e.message}")
        return create_error_response(
            message="Ошибка обработки файла",
            error_code=e.error_code,
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка загрузки файла {file_type} пользователем {current_user.id}: {str(e)}")
        return create_error_response(
            message="Внутренняя ошибка сервера",
            error_code="INTERNAL_SERVER_ERROR",
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        )

@router.post('/avatar', response_model=dict)
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
        dict: Стандартизированный ответ
    """
    try:
        logger.info(f"Загрузка аватара пользователем {current_user.id}")
        
        # Читаем данные файла
        file_data = await file.read()
        
        # Обрабатываем файл
        result = file_handler.process_file(file_data, file.filename, 'avatar', current_user.id)
        
        # Обновляем профиль пользователя
        current_user.avatar_url = result['file_url']
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Аватар успешно загружен пользователем {current_user.id}: {result['file_url']}")
        
        return create_success_response(
            data={
                'file_url': result['file_url'],
                'file_type': 'avatar',
                'original_filename': result['original_filename'],
                'file_size': result['file_size'],
                'file_hash': result['file_hash'],
                'mime_type': result['mime_type']
            },
            message="Аватар успешно загружен"
        )
        
    except FileValidationError as e:
        logger.warning(f"Ошибка валидации аватара пользователем {current_user.id}: {e.message}")
        return create_validation_error_response(
            field_errors={'file': [e.message]},
            message="Ошибка валидации аватара",
            request_id=str(uuid.uuid4())
        )
        
    except FileProcessingError as e:
        logger.error(f"Ошибка обработки аватара пользователем {current_user.id}: {e.message}")
        return create_error_response(
            message="Ошибка обработки аватара",
            error_code=e.error_code,
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка загрузки аватара пользователем {current_user.id}: {str(e)}")
        return create_error_response(
            message="Внутренняя ошибка сервера",
            error_code="INTERNAL_SERVER_ERROR",
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        )

@router.post('/driver-license', response_model=dict)
async def upload_driver_license(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Загрузка водительского удостоверения
    
    Args:
        file: Файл изображения или PDF
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        logger.info(f"Загрузка водительского удостоверения пользователем {current_user.id}")
        
        # Читаем данные файла
        file_data = await file.read()
        
        # Обрабатываем файл
        result = file_handler.process_file(file_data, file.filename, 'license', current_user.id)
        
        # Обновляем профиль пользователя
        current_user.driver_license_photo_url = result['file_url']
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Водительское удостоверение успешно загружено пользователем {current_user.id}: {result['file_url']}")
        
        return create_success_response(
            data={
                'file_url': result['file_url'],
                'file_type': 'license',
                'original_filename': result['original_filename'],
                'file_size': result['file_size'],
                'file_hash': result['file_hash'],
                'mime_type': result['mime_type']
            },
            message="Водительское удостоверение успешно загружено"
        )
        
    except FileValidationError as e:
        logger.warning(f"Ошибка валидации водительского удостоверения пользователем {current_user.id}: {e.message}")
        return create_validation_error_response(
            field_errors={'file': [e.message]},
            message="Ошибка валидации водительского удостоверения",
            request_id=str(uuid.uuid4())
        )
        
    except FileProcessingError as e:
        logger.error(f"Ошибка обработки водительского удостоверения пользователем {current_user.id}: {e.message}")
        return create_error_response(
            message="Ошибка обработки водительского удостоверения",
            error_code=e.error_code,
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка загрузки водительского удостоверения пользователем {current_user.id}: {str(e)}")
        return create_error_response(
            message="Внутренняя ошибка сервера",
            error_code="INTERNAL_SERVER_ERROR",
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        )

@router.post('/car-photo', response_model=dict)
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
        dict: Стандартизированный ответ
    """
    try:
        logger.info(f"Загрузка фото автомобиля пользователем {current_user.id}")
        
        # Читаем данные файла
        file_data = await file.read()
        
        # Обрабатываем файл
        result = file_handler.process_file(file_data, file.filename, 'car', current_user.id)
        
        # Обновляем профиль пользователя
        current_user.car_photo_url = result['file_url']
        current_user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Фото автомобиля успешно загружено пользователем {current_user.id}: {result['file_url']}")
        
        return create_success_response(
            data={
                'file_url': result['file_url'],
                'file_type': 'car',
                'original_filename': result['original_filename'],
                'file_size': result['file_size'],
                'file_hash': result['file_hash'],
                'mime_type': result['mime_type']
            },
            message="Фото автомобиля успешно загружено"
        )
        
    except FileValidationError as e:
        logger.warning(f"Ошибка валидации фото автомобиля пользователем {current_user.id}: {e.message}")
        return create_validation_error_response(
            field_errors={'file': [e.message]},
            message="Ошибка валидации фото автомобиля",
            request_id=str(uuid.uuid4())
        )
        
    except FileProcessingError as e:
        logger.error(f"Ошибка обработки фото автомобиля пользователем {current_user.id}: {e.message}")
        return create_error_response(
            message="Ошибка обработки фото автомобиля",
            error_code=e.error_code,
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка загрузки фото автомобиля пользователем {current_user.id}: {str(e)}")
        return create_error_response(
            message="Внутренняя ошибка сервера",
            error_code="INTERNAL_SERVER_ERROR",
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        )

@router.delete('/{file_type}/{filename}', response_model=dict)
async def delete_file(
    file_type: str,
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаление файла
    
    Args:
        file_type: Тип файла
        filename: Имя файла
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        logger.info(f"Удаление файла {file_type}/{filename} пользователем {current_user.id}")
        
        # Формируем URL файла
        file_url = f"/uploads/{file_type}/{filename}"
        
        # Удаляем файл
        success = file_handler.delete_file(file_url, current_user.id)
        
        if success:
            # Обновляем профиль пользователя
            if file_type == 'avatars':
                current_user.avatar_url = None
            elif file_type == 'licenses':
                current_user.driver_license_photo_url = None
            elif file_type == 'cars':
                current_user.car_photo_url = None
            
            current_user.updated_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Файл {file_type}/{filename} успешно удален пользователем {current_user.id}")
            
            return create_success_response(
                message="Файл успешно удален"
            )
        else:
            logger.warning(f"Не удалось удалить файл {file_type}/{filename} пользователем {current_user.id}")
            
            return create_error_response(
                message="Файл не найден или не может быть удален",
                error_code="FILE_NOT_FOUND",
                user_id=current_user.id,
                request_id=str(uuid.uuid4())
            )
        
    except Exception as e:
        logger.error(f"Ошибка удаления файла {file_type}/{filename} пользователем {current_user.id}: {str(e)}")
        return create_error_response(
            message="Ошибка удаления файла",
            error_code="DELETE_ERROR",
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        )

@router.get('/info/{file_type}/{filename}', response_model=dict)
async def get_file_info(
    file_type: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Получение информации о файле
    
    Args:
        file_type: Тип файла
        filename: Имя файла
        current_user: Текущий пользователь
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        logger.info(f"Получение информации о файле {file_type}/{filename} пользователем {current_user.id}")
        
        # Формируем URL файла
        file_url = f"/uploads/{file_type}/{filename}"
        
        # Получаем информацию о файле
        file_info = file_handler.get_file_info(file_url)
        
        if file_info:
            logger.info(f"Информация о файле {file_type}/{filename} получена пользователем {current_user.id}")
            
            return create_success_response(
                data=file_info,
                message="Информация о файле получена"
            )
        else:
            logger.warning(f"Файл {file_type}/{filename} не найден пользователем {current_user.id}")
            
            return create_error_response(
                message="Файл не найден",
                error_code="FILE_NOT_FOUND",
                user_id=current_user.id,
                request_id=str(uuid.uuid4())
            )
        
    except Exception as e:
        logger.error(f"Ошибка получения информации о файле {file_type}/{filename} пользователем {current_user.id}: {str(e)}")
        return create_error_response(
            message="Ошибка получения информации о файле",
            error_code="INFO_ERROR",
            user_id=current_user.id,
            request_id=str(uuid.uuid4())
        ) 