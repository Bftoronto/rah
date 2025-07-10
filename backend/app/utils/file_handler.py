"""
Улучшенный обработчик файлов с детальной обработкой ошибок
"""

import os
import uuid
import hashlib
import mimetypes
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime
import logging
from PIL import Image
import magic
import io

from ..utils.logger import get_logger
from ..utils.error_handler import api_error_handler
from ..schemas.responses import create_error_response, create_success_response

logger = get_logger("file_handler")

class FileValidationError(Exception):
    """Кастомное исключение для ошибок валидации файлов"""
    def __init__(self, message: str, error_code: str = "FILE_VALIDATION_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class FileProcessingError(Exception):
    """Кастомное исключение для ошибок обработки файлов"""
    def __init__(self, message: str, error_code: str = "FILE_PROCESSING_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class FileHandler:
    """Улучшенный обработчик файлов"""
    
    # Конфигурация типов файлов
    FILE_CONFIGS = {
        'avatar': {
            'allowed_types': ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
            'max_size': 5 * 1024 * 1024,  # 5MB
            'max_dimensions': (1024, 1024),
            'directory': 'avatars',
            'compress': True
        },
        'license': {
            'allowed_types': ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'],
            'max_size': 10 * 1024 * 1024,  # 10MB
            'max_dimensions': (2048, 2048),
            'directory': 'licenses',
            'compress': True
        },
        'car': {
            'allowed_types': ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'],
            'max_size': 8 * 1024 * 1024,  # 8MB
            'max_dimensions': (2048, 2048),
            'directory': 'cars',
            'compress': True
        },
        'document': {
            'allowed_types': ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
            'max_size': 15 * 1024 * 1024,  # 15MB
            'max_dimensions': None,
            'directory': 'documents',
            'compress': False
        }
    }
    
    def __init__(self, upload_dir: str):
        self.upload_dir = upload_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Создает необходимые директории"""
        for config in self.FILE_CONFIGS.values():
            dir_path = Path(self.upload_dir) / config['directory']
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, file_data: bytes, filename: str, file_type: str) -> Dict[str, Any]:
        """
        Детальная валидация файла
        
        Args:
            file_data: Данные файла
            filename: Имя файла
            file_type: Тип файла
            
        Returns:
            Dict[str, Any]: Информация о файле
            
        Raises:
            FileValidationError: При ошибке валидации
        """
        try:
            # Проверяем тип файла
            if file_type not in self.FILE_CONFIGS:
                raise FileValidationError(
                    f"Неподдерживаемый тип файла: {file_type}",
                    "INVALID_FILE_TYPE"
                )
            
            config = self.FILE_CONFIGS[file_type]
            
            # Определяем MIME тип
            mime_type = magic.from_buffer(file_data, mime=True)
            
            # Проверяем разрешенные типы
            if mime_type not in config['allowed_types']:
                raise FileValidationError(
                    f"Неподдерживаемый MIME тип: {mime_type}. Разрешены: {', '.join(config['allowed_types'])}",
                    "INVALID_MIME_TYPE"
                )
            
            # Проверяем размер файла
            file_size = len(file_data)
            if file_size > config['max_size']:
                max_size_mb = config['max_size'] / (1024 * 1024)
                raise FileValidationError(
                    f"Размер файла ({file_size / (1024 * 1024):.1f}MB) превышает максимально допустимый ({max_size_mb}MB)",
                    "FILE_TOO_LARGE"
                )
            
            # Проверяем минимальный размер (защита от пустых файлов)
            if file_size < 100:  # Минимум 100 байт
                raise FileValidationError(
                    "Файл слишком маленький или поврежден",
                    "FILE_TOO_SMALL"
                )
            
            # Проверяем расширение файла
            file_extension = Path(filename).suffix.lower()
            expected_extensions = {
                'image/jpeg': ['.jpg', '.jpeg'],
                'image/png': ['.png'],
                'image/webp': ['.webp'],
                'application/pdf': ['.pdf'],
                'application/msword': ['.doc'],
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
            }
            
            if mime_type in expected_extensions and file_extension not in expected_extensions[mime_type]:
                raise FileValidationError(
                    f"Несоответствие расширения файла ({file_extension}) и MIME типа ({mime_type})",
                    "INVALID_FILE_EXTENSION"
                )
            
            # Проверяем изображения на размеры
            if mime_type.startswith('image/') and config['max_dimensions']:
                try:
                    image = Image.open(io.BytesIO(file_data))
                    width, height = image.size
                    max_width, max_height = config['max_dimensions']
                    
                    if width > max_width or height > max_height:
                        raise FileValidationError(
                            f"Размеры изображения ({width}x{height}) превышают максимально допустимые ({max_width}x{max_height})",
                            "IMAGE_TOO_LARGE"
                        )
                    
                    # Проверяем на вредоносные изображения (bomb files)
                    if width * height > 100000000:  # 100MP
                        raise FileValidationError(
                            "Изображение слишком большое и может быть вредоносным",
                            "SUSPICIOUS_IMAGE"
                        )
                        
                except Exception as e:
                    if "cannot identify image file" in str(e).lower():
                        raise FileValidationError(
                            "Файл не является корректным изображением",
                            "INVALID_IMAGE"
                        )
                    raise FileValidationError(
                        f"Ошибка обработки изображения: {str(e)}",
                        "IMAGE_PROCESSING_ERROR"
                    )
            
            # Проверяем на вредоносные файлы
            if self._is_suspicious_file(file_data, filename):
                raise FileValidationError(
                    "Файл может быть вредоносным",
                    "SUSPICIOUS_FILE"
                )
            
            return {
                'mime_type': mime_type,
                'file_size': file_size,
                'filename': filename,
                'file_type': file_type,
                'is_image': mime_type.startswith('image/'),
                'config': config
            }
            
        except FileValidationError:
            raise
        except Exception as e:
            logger.error(f"Ошибка валидации файла: {str(e)}")
            raise FileValidationError(
                f"Ошибка валидации файла: {str(e)}",
                "VALIDATION_ERROR"
            )
    
    def _is_suspicious_file(self, file_data: bytes, filename: str) -> bool:
        """Проверяет файл на подозрительность"""
        # Проверяем на исполняемые файлы
        executable_signatures = [
            b'MZ',  # Windows PE
            b'\x7fELF',  # Linux ELF
            b'\xfe\xed\xfa',  # macOS Mach-O
        ]
        
        for signature in executable_signatures:
            if file_data.startswith(signature):
                return True
        
        # Проверяем расширения
        suspicious_extensions = ['.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js']
        file_extension = Path(filename).suffix.lower()
        
        if file_extension in suspicious_extensions:
            return True
        
        # Проверяем на слишком большие файлы
        if len(file_data) > 50 * 1024 * 1024:  # 50MB
            return True
        
        return False
    
    def process_file(self, file_data: bytes, filename: str, file_type: str, user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает и сохраняет файл
        
        Args:
            file_data: Данные файла
            filename: Имя файла
            file_type: Тип файла
            user_id: ID пользователя
            
        Returns:
            Dict[str, Any]: Информация о сохраненном файле
        """
        try:
            # Валидируем файл
            file_info = self.validate_file(file_data, filename, file_type)
            config = file_info['config']
            
            # Генерируем уникальное имя файла
            file_extension = Path(filename).suffix
            unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_extension}"
            
            # Определяем путь сохранения
            save_dir = Path(self.upload_dir) / config['directory']
            save_path = save_dir / unique_filename
            
            # Обрабатываем изображения если нужно
            if file_info['is_image'] and config['compress']:
                processed_data = self._compress_image(file_data, config['max_dimensions'])
            else:
                processed_data = file_data
            
            # Сохраняем файл
            with open(save_path, 'wb') as f:
                f.write(processed_data)
            
            # Вычисляем хеш файла
            file_hash = hashlib.md5(processed_data).hexdigest()
            
            # Формируем URL
            relative_path = save_path.relative_to(Path(self.upload_dir))
            file_url = f"/uploads/{relative_path}"
            
            return {
                'file_url': str(file_url),
                'file_type': file_type,
                'original_filename': filename,
                'saved_filename': unique_filename,
                'file_size': len(processed_data),
                'file_hash': file_hash,
                'mime_type': file_info['mime_type'],
                'save_path': str(save_path),
                'user_id': user_id,
                'uploaded_at': datetime.now()
            }
            
        except FileValidationError:
            raise
        except Exception as e:
            logger.error(f"Ошибка обработки файла: {str(e)}")
            raise FileProcessingError(
                f"Ошибка обработки файла: {str(e)}",
                "PROCESSING_ERROR"
            )
    
    def _compress_image(self, image_data: bytes, max_dimensions: Tuple[int, int]) -> bytes:
        """Сжимает изображение"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Конвертируем в RGB если нужно
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Изменяем размер если нужно
            if image.size[0] > max_dimensions[0] or image.size[1] > max_dimensions[1]:
                image.thumbnail(max_dimensions, Image.Resampling.LANCZOS)
            
            # Сохраняем с оптимизацией
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Ошибка сжатия изображения: {str(e)}")
            return image_data  # Возвращаем оригинал если сжатие не удалось
    
    def delete_file(self, file_url: str, user_id: int) -> bool:
        """
        Удаляет файл
        
        Args:
            file_url: URL файла
            user_id: ID пользователя
            
        Returns:
            bool: Успешность удаления
        """
        try:
            # Извлекаем путь из URL
            if file_url.startswith('/uploads/'):
                relative_path = file_url[8:]  # Убираем '/uploads/'
                file_path = Path(self.upload_dir) / relative_path
            else:
                file_path = Path(file_url)
            
            # Проверяем что файл существует и принадлежит пользователю
            if not file_path.exists():
                logger.warning(f"Файл не найден: {file_path}")
                return False
            
            # Проверяем что файл принадлежит пользователю
            filename = file_path.name
            if not filename.startswith(f"{user_id}_"):
                logger.warning(f"Попытка удаления чужого файла: {filename} пользователем {user_id}")
                return False
            
            # Удаляем файл
            file_path.unlink()
            logger.info(f"Файл удален: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка удаления файла: {str(e)}")
            return False
    
    def get_file_info(self, file_url: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о файле
        
        Args:
            file_url: URL файла
            
        Returns:
            Optional[Dict[str, Any]]: Информация о файле
        """
        try:
            if file_url.startswith('/uploads/'):
                relative_path = file_url[8:]
                file_path = Path(self.upload_dir) / relative_path
            else:
                file_path = Path(file_url)
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            return {
                'file_url': file_url,
                'file_path': str(file_path),
                'file_size': stat.st_size,
                'created_at': datetime.fromtimestamp(stat.st_ctime),
                'modified_at': datetime.fromtimestamp(stat.st_mtime),
                'exists': True
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о файле: {str(e)}")
            return None

# Глобальный экземпляр обработчика файлов
file_handler = None

def get_file_handler(upload_dir: str) -> FileHandler:
    """Получает глобальный экземпляр обработчика файлов"""
    global file_handler
    if file_handler is None:
        file_handler = FileHandler(upload_dir)
    return file_handler 