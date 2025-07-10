import os
import uuid
import mimetypes
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from ..models.upload import Upload
from ..models.user import User
from ..utils.error_handler import error_handler
from ..utils.logger import get_logger
from ..validators.data_validator import DataValidator
from ..config.settings import settings

logger = get_logger("upload_service")

class UploadService:
    """Сервис для работы с загрузкой файлов"""
    
    def __init__(self, db: Session):
        self.db = db
        self.validator = DataValidator()
        
        # Создаем директорию для загрузок если не существует
        os.makedirs(settings.upload_dir, exist_ok=True)
    
    @error_handler.handle_database_operation("upload_file")
    async def upload_file(self, file: UploadFile, user_id: int, file_type: str = "general") -> Dict[str, Any]:
        """Загрузка файла с валидацией и сохранением"""
        try:
            # Проверяем существование пользователя
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Валидируем файл
            await self._validate_file(file, file_type)
            
            # Генерируем уникальное имя файла
            file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Создаем путь для сохранения
            file_path = os.path.join(settings.upload_dir, unique_filename)
            
            # Сохраняем файл
            content = await file.read()
            
            # Проверяем размер файла
            self.validator.validate_file_size(len(content))
            
            # Сохраняем файл на диск
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Определяем MIME тип
            mime_type, _ = mimetypes.guess_type(file.filename or "")
            
            # Создаем запись в базе данных
            upload_record = Upload(
                user_id=user_id,
                original_filename=file.filename or "unknown",
                stored_filename=unique_filename,
                file_path=file_path,
                file_size=len(content),
                mime_type=mime_type or "application/octet-stream",
                file_type=file_type,
                upload_date=datetime.now()
            )
            
            self.db.add(upload_record)
            self.db.commit()
            self.db.refresh(upload_record)
            
            # Формируем ответ
            upload_data = {
                "id": upload_record.id,
                "original_filename": upload_record.original_filename,
                "stored_filename": upload_record.stored_filename,
                "file_size": upload_record.file_size,
                "mime_type": upload_record.mime_type,
                "file_type": upload_record.file_type,
                "upload_date": upload_record.upload_date.isoformat(),
                "download_url": f"/uploads/{unique_filename}"
            }
            
            logger.info(f"Файл {file.filename} успешно загружен пользователем {user_id}")
            return upload_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка загрузки файла пользователем {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка загрузки файла"
            )
    
    async def _validate_file(self, file: UploadFile, file_type: str) -> None:
        """Валидация загружаемого файла"""
        try:
            # Проверяем, что файл не пустой
            if not file.filename:
                raise ValueError("Имя файла не может быть пустым")
            
            # Проверяем размер файла
            content = await file.read()
            await file.seek(0)  # Возвращаем указатель в начало
            
            self.validator.validate_file_size(len(content))
            
            # Определяем MIME тип
            mime_type, _ = mimetypes.guess_type(file.filename)
            
            # Валидируем тип файла в зависимости от file_type
            if file_type == "avatar":
                allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
                max_size = 5 * 1024 * 1024  # 5MB
            elif file_type == "car_photo":
                allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
                max_size = 10 * 1024 * 1024  # 10MB
            elif file_type == "driver_license":
                allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"]
                max_size = 10 * 1024 * 1024  # 10MB
            elif file_type == "document":
                allowed_types = ["application/pdf", "application/msword", 
                               "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                               "image/jpeg", "image/png"]
                max_size = 20 * 1024 * 1024  # 20MB
            else:  # general
                allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp", 
                               "application/pdf", "text/plain"]
                max_size = 10 * 1024 * 1024  # 10MB
            
            # Проверяем размер файла для конкретного типа
            if len(content) > max_size:
                raise ValueError(f"Размер файла превышает {max_size / (1024 * 1024)}MB для типа {file_type}")
            
            # Проверяем MIME тип
            if mime_type and mime_type not in allowed_types:
                raise ValueError(f"Неподдерживаемый тип файла: {mime_type}")
            
            # Дополнительные проверки для изображений
            if mime_type and mime_type.startswith("image/"):
                # Проверяем расширение файла
                file_extension = os.path.splitext(file.filename)[1].lower()
                allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
                
                if file_extension not in allowed_extensions:
                    raise ValueError(f"Неподдерживаемое расширение файла: {file_extension}")
            
        except ValueError as e:
            logger.warning(f"Ошибка валидации файла {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
    
    @error_handler.handle_database_operation("get_uploads")
    def get_uploads(self, user_id: int, file_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Получение файлов пользователя"""
        try:
            # Проверяем существование пользователя
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Формируем запрос
            query = self.db.query(Upload).filter(Upload.user_id == user_id)
            
            # Фильтруем по типу файла если указан
            if file_type:
                query = query.filter(Upload.file_type == file_type)
            
            # Получаем файлы с сортировкой по дате загрузки
            uploads = query.order_by(Upload.upload_date.desc()).limit(limit).all()
            
            # Формируем ответ
            uploads_data = []
            for upload in uploads:
                upload_data = {
                    "id": upload.id,
                    "original_filename": upload.original_filename,
                    "stored_filename": upload.stored_filename,
                    "file_size": upload.file_size,
                    "mime_type": upload.mime_type,
                    "file_type": upload.file_type,
                    "upload_date": upload.upload_date.isoformat(),
                    "download_url": f"/uploads/{upload.stored_filename}"
                }
                uploads_data.append(upload_data)
            
            logger.info(f"Получено {len(uploads_data)} файлов пользователя {user_id}")
            return uploads_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения файлов пользователя {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка получения файлов"
            )
    
    @error_handler.handle_database_operation("get_upload")
    def get_upload(self, upload_id: int, user_id: int) -> Dict[str, Any]:
        """Получение конкретного файла пользователя"""
        try:
            # Получаем файл
            upload = self.db.query(Upload).filter(
                Upload.id == upload_id,
                Upload.user_id == user_id
            ).first()
            
            if not upload:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Файл не найден"
                )
            
            # Проверяем существование файла на диске
            if not os.path.exists(upload.file_path):
                logger.warning(f"Файл {upload.file_path} не найден на диске")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Файл не найден на сервере"
                )
            
            upload_data = {
                "id": upload.id,
                "original_filename": upload.original_filename,
                "stored_filename": upload.stored_filename,
                "file_size": upload.file_size,
                "mime_type": upload.mime_type,
                "file_type": upload.file_type,
                "upload_date": upload.upload_date.isoformat(),
                "download_url": f"/uploads/{upload.stored_filename}"
            }
            
            logger.info(f"Файл {upload_id} получен пользователем {user_id}")
            return upload_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения файла {upload_id} пользователем {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка получения файла"
            )
    
    @error_handler.handle_database_operation("delete_upload")
    def delete_upload(self, upload_id: int, user_id: int) -> bool:
        """Удаление файла пользователя"""
        try:
            # Получаем файл
            upload = self.db.query(Upload).filter(
                Upload.id == upload_id,
                Upload.user_id == user_id
            ).first()
            
            if not upload:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Файл не найден"
                )
            
            # Удаляем файл с диска
            if os.path.exists(upload.file_path):
                os.remove(upload.file_path)
                logger.info(f"Файл {upload.file_path} удален с диска")
            
            # Удаляем запись из базы данных
            self.db.delete(upload)
            self.db.commit()
            
            logger.info(f"Файл {upload_id} удален пользователем {user_id}")
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка удаления файла {upload_id} пользователем {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка удаления файла"
            )
    
    def get_upload_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики загрузок пользователя"""
        try:
            # Проверяем существование пользователя
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Пользователь не найден"
                )
            
            # Получаем статистику
            total_uploads = self.db.query(Upload).filter(Upload.user_id == user_id).count()
            total_size = self.db.query(Upload.file_size).filter(Upload.user_id == user_id).all()
            total_size_bytes = sum(size[0] for size in total_size if size[0])
            
            # Статистика по типам файлов
            type_stats = self.db.query(
                Upload.file_type,
                Upload.file_size
            ).filter(Upload.user_id == user_id).all()
            
            type_counts = {}
            type_sizes = {}
            
            for file_type, file_size in type_stats:
                type_counts[file_type] = type_counts.get(file_type, 0) + 1
                type_sizes[file_type] = type_sizes.get(file_type, 0) + (file_size or 0)
            
            stats = {
                "user_id": user_id,
                "total_uploads": total_uploads,
                "total_size_bytes": total_size_bytes,
                "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
                "type_counts": type_counts,
                "type_sizes_mb": {k: round(v / (1024 * 1024), 2) for k, v in type_sizes.items()}
            }
            
            logger.info(f"Статистика загрузок пользователя {user_id} получена")
            return stats
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения статистики загрузок пользователя {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка получения статистики загрузок"
            ) 