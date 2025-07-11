#!/usr/bin/env python3
"""
ЭКСТРЕННЫЙ СКРИПТ ВОССТАНОВЛЕНИЯ
Проблема: ImportError: failed to find libmagic. Check your installation

Автор: AI Assistant
Дата: 2025-07-10
Версия: 1.0
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def log(message: str, level: str = "INFO"):
    """Логирование с временными метками"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def check_system():
    """Проверка системы"""
    log("🔍 Проверка системы...")
    
    # Проверяем ОС
    import platform
    os_name = platform.system()
    log(f"Операционная система: {os_name}")
    
    # Проверяем Python
    python_version = sys.version
    log(f"Версия Python: {python_version}")
    
    # Проверяем наличие libmagic
    try:
        import magic
        log("✅ python-magic установлен")
        return True
    except ImportError as e:
        log(f"❌ python-magic не установлен: {e}")
        return False

def install_libmagic_ubuntu():
    """Установка libmagic на Ubuntu/Debian"""
    log("📦 Установка libmagic на Ubuntu/Debian...")
    
    commands = [
        "apt-get update",
        "apt-get install -y libmagic1 libmagic-dev",
        "apt-get clean"
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            log(f"✅ Выполнено: {cmd}")
        except subprocess.CalledProcessError as e:
            log(f"❌ Ошибка выполнения {cmd}: {e}", "ERROR")
            return False
    
    return True

def install_libmagic_centos():
    """Установка libmagic на CentOS/RHEL"""
    log("📦 Установка libmagic на CentOS/RHEL...")
    
    commands = [
        "yum update -y",
        "yum install -y file-devel",
        "yum clean all"
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            log(f"✅ Выполнено: {cmd}")
        except subprocess.CalledProcessError as e:
            log(f"❌ Ошибка выполнения {cmd}: {e}", "ERROR")
            return False
    
    return True

def install_libmagic_alpine():
    """Установка libmagic на Alpine"""
    log("📦 Установка libmagic на Alpine...")
    
    commands = [
        "apk update",
        "apk add file-dev",
        "apk cache clean"
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            log(f"✅ Выполнено: {cmd}")
        except subprocess.CalledProcessError as e:
            log(f"❌ Ошибка выполнения {cmd}: {e}", "ERROR")
            return False
    
    return True

def install_python_magic():
    """Установка python-magic"""
    log("🐍 Установка python-magic...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "python-magic"], check=True)
        log("✅ python-magic установлен")
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ Ошибка установки python-magic: {e}", "ERROR")
        return False

def create_alternative_file_handler():
    """Создание альтернативного обработчика файлов"""
    log("🔧 Создание альтернативного обработчика файлов...")
    
    # Проверяем существование файла
    file_handler_path = Path("backend/app/utils/file_handler.py")
    alternative_path = Path("backend/app/utils/file_handler_alternative.py")
    
    if not file_handler_path.exists():
        log("❌ Файл file_handler.py не найден", "ERROR")
        return False
    
    if alternative_path.exists():
        log("✅ Альтернативный обработчик уже существует")
        return True
    
    # Создаем альтернативный файл
    alternative_content = '''"""
Альтернативный обработчик файлов без зависимости от python-magic
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
    """Улучшенный обработчик файлов без python-magic"""
    
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
    
    def _detect_mime_type(self, file_data: bytes, filename: str) -> str:
        """
        Определяет MIME тип файла без использования python-magic
        """
        # Определяем по расширению файла
        file_extension = Path(filename).suffix.lower()
        
        # Маппинг расширений на MIME типы
        extension_mime_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        
        if file_extension in extension_mime_map:
            return extension_mime_map[file_extension]
        
        # Дополнительная проверка для изображений по сигнатурам
        if len(file_data) >= 4:
            # JPEG
            if file_data[:2] == b'\\xff\\xd8':
                return 'image/jpeg'
            # PNG
            if file_data[:8] == b'\\x89PNG\\r\\n\\x1a\\n':
                return 'image/png'
            # WebP
            if file_data[:4] == b'RIFF' and file_data[8:12] == b'WEBP':
                return 'image/webp'
            # PDF
            if file_data[:4] == b'%PDF':
                return 'application/pdf'
        
        # Fallback на определение по расширению через mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    def validate_file(self, file_data: bytes, filename: str, file_type: str) -> Dict[str, Any]:
        """
        Детальная валидация файла
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
            mime_type = self._detect_mime_type(file_data, filename)
            
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
                f"Неожиданная ошибка валидации: {str(e)}",
                "VALIDATION_ERROR"
            )
    
    def process_file(self, file_data: bytes, filename: str, file_type: str, user_id: int) -> Dict[str, Any]:
        """
        Обрабатывает и сохраняет файл
        """
        try:
            # Валидируем файл
            validation_info = self.validate_file(file_data, filename, file_type)
            
            # Генерируем уникальное имя файла
            file_extension = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Определяем путь сохранения
            config = validation_info['config']
            save_dir = Path(self.upload_dir) / config['directory']
            save_path = save_dir / unique_filename
            
            # Сохраняем файл
            with open(save_path, 'wb') as f:
                f.write(file_data)
            
            # Вычисляем хеш файла
            file_hash = hashlib.md5(file_data).hexdigest()
            
            # Формируем URL
            file_url = f"/uploads/{config['directory']}/{unique_filename}"
            
            return {
                'file_url': file_url,
                'filename': unique_filename,
                'original_filename': filename,
                'file_size': len(file_data),
                'mime_type': validation_info['mime_type'],
                'file_hash': file_hash,
                'user_id': user_id,
                'uploaded_at': datetime.utcnow().isoformat(),
                'file_type': file_type
            }
            
        except FileValidationError:
            raise
        except Exception as e:
            logger.error(f"Ошибка обработки файла: {str(e)}")
            raise FileProcessingError(
                f"Ошибка сохранения файла: {str(e)}",
                "SAVE_ERROR"
            )

def get_file_handler(upload_dir: str) -> FileHandler:
    """
    Фабричная функция для создания обработчика файлов
    """
    return FileHandler(upload_dir)
'''
    
    try:
        with open(alternative_path, 'w', encoding='utf-8') as f:
            f.write(alternative_content)
        log("✅ Альтернативный обработчик файлов создан")
        return True
    except Exception as e:
        log(f"❌ Ошибка создания альтернативного обработчика: {e}", "ERROR")
        return False

def update_imports():
    """Обновление импортов для использования альтернативного обработчика"""
    log("🔄 Обновление импортов...")
    
    # Файлы, которые импортируют file_handler
    files_to_update = [
        "backend/app/api/upload.py"
    ]
    
    for file_path in files_to_update:
        if not Path(file_path).exists():
            log(f"⚠️ Файл {file_path} не найден")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Заменяем импорт
            old_import = "from ..utils.file_handler import get_file_handler, FileValidationError, FileProcessingError"
            new_import = "from ..utils.file_handler_alternative import get_file_handler, FileValidationError, FileProcessingError"
            
            if old_import in content:
                content = content.replace(old_import, new_import)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                log(f"✅ Обновлен импорт в {file_path}")
            else:
                log(f"⚠️ Импорт не найден в {file_path}")
                
        except Exception as e:
            log(f"❌ Ошибка обновления {file_path}: {e}", "ERROR")

def test_application():
    """Тестирование приложения"""
    log("🧪 Тестирование приложения...")
    
    try:
        # Проверяем импорт основного модуля
        import sys
        sys.path.append('backend')
        
        from app.main import app
        log("✅ Приложение успешно импортировано")
        
        # Проверяем доступность эндпоинтов
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Тестируем health check
        response = client.get("/health")
        if response.status_code == 200:
            log("✅ Health check работает")
        else:
            log(f"⚠️ Health check вернул статус {response.status_code}")
        
        return True
        
    except Exception as e:
        log(f"❌ Ошибка тестирования приложения: {e}", "ERROR")
        return False

def main():
    """Основная функция восстановления"""
    log("🚨 ЗАПУСК ЭКСТРЕННОГО ВОССТАНОВЛЕНИЯ")
    log("=" * 50)
    
    # Шаг 1: Проверка системы
    if check_system():
        log("✅ Система готова к работе")
    else:
        log("⚠️ Обнаружены проблемы с системой")
    
    # Шаг 2: Попытка установки libmagic
    import platform
    os_name = platform.system().lower()
    
    if os_name in ['linux', 'darwin']:
        # Определяем дистрибутив Linux
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read().lower()
            
            if 'ubuntu' in os_info or 'debian' in os_info:
                install_libmagic_ubuntu()
            elif 'centos' in os_info or 'rhel' in os_info or 'redhat' in os_info:
                install_libmagic_centos()
            elif 'alpine' in os_info:
                install_libmagic_alpine()
            else:
                log("⚠️ Неизвестный дистрибутив Linux")
        except FileNotFoundError:
            log("⚠️ Не удалось определить дистрибутив Linux")
    
    # Шаг 3: Установка python-magic
    install_python_magic()
    
    # Шаг 4: Создание альтернативного обработчика
    create_alternative_file_handler()
    
    # Шаг 5: Обновление импортов
    update_imports()
    
    # Шаг 6: Тестирование
    test_application()
    
    log("=" * 50)
    log("🎉 ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО")
    log("📋 РЕКОМЕНДАЦИИ:")
    log("1. Перезапустите Docker контейнер")
    log("2. Проверьте логи приложения")
    log("3. Протестируйте загрузку файлов")
    log("4. При необходимости используйте альтернативный обработчик")

if __name__ == "__main__":
    main() 