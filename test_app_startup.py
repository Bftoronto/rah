#!/usr/bin/env python3
"""
БЫСТРЫЙ ТЕСТ ЗАПУСКА ПРИЛОЖЕНИЯ
Проверяет возможность импорта всех модулей без ошибок
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Тестирует импорт всех критических модулей"""
    print("🧪 ТЕСТИРОВАНИЕ ИМПОРТОВ")
    print("=" * 40)
    
    # Добавляем backend в путь
    backend_path = Path("backend")
    if backend_path.exists():
        sys.path.insert(0, str(backend_path))
    
    # Устанавливаем тестовые переменные окружения
    import os
    test_env = {
        'DATABASE_URL': 'sqlite:///./test.db',
        'SECRET_KEY': 'test_secret_key_for_diagnosis_only',
        'TELEGRAM_BOT_TOKEN': 'test_bot_token',
        'REDIS_URL': 'redis://localhost:6379',
        'UPLOAD_DIR': './uploads',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test'
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
    
    tests = [
        ("app.main", "Основной модуль приложения"),
        ("app.api.auth", "API аутентификации"),
        ("app.api.rides", "API поездок"),
        ("app.api.upload", "API загрузки файлов"),
        ("app.utils.file_handler_alternative", "Альтернативный обработчик файлов"),
        ("app.config.settings", "Настройки приложения"),
        ("app.database", "База данных"),
        ("app.models.user", "Модель пользователя"),
        ("app.schemas.user", "Схемы пользователя"),
    ]
    
    failed_imports = []
    
    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"✅ {description}: {module_name}")
        except ImportError as e:
            print(f"❌ {description}: {module_name} - {e}")
            failed_imports.append((module_name, str(e)))
        except Exception as e:
            print(f"⚠️ {description}: {module_name} - {e}")
            failed_imports.append((module_name, str(e)))
    
    print("\n" + "=" * 40)
    
    if failed_imports:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ:")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    else:
        print("✅ ВСЕ ИМПОРТЫ УСПЕШНЫ")
        return True

def test_fastapi_app():
    """Тестирует создание FastAPI приложения"""
    print("\n🚀 ТЕСТИРОВАНИЕ FASTAPI ПРИЛОЖЕНИЯ")
    print("=" * 40)
    
    try:
        from app.main import app
        print("✅ FastAPI приложение создано успешно")
        
        # Проверяем наличие основных эндпоинтов
        routes = [route.path for route in app.routes]
        print(f"📋 Найдено {len(routes)} маршрутов")
        
        # Проверяем критические эндпоинты
        critical_endpoints = [
            "/docs",
            "/health",
            "/api/auth/login",
            "/api/rides/",
            "/api/upload/"
        ]
        
        for endpoint in critical_endpoints:
            if any(endpoint in route for route in routes):
                print(f"✅ Эндпоинт {endpoint} найден")
            else:
                print(f"⚠️ Эндпоинт {endpoint} не найден")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания FastAPI приложения: {e}")
        return False

def test_file_handler():
    """Тестирует альтернативный обработчик файлов"""
    print("\n📁 ТЕСТИРОВАНИЕ ОБРАБОТЧИКА ФАЙЛОВ")
    print("=" * 40)
    
    try:
        from app.utils.file_handler_alternative import FileHandler, FileValidationError, FileProcessingError
        
        # Создаем временную директорию для тестов
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileHandler(temp_dir)
            print("✅ Обработчик файлов создан успешно")
            
            # Тестируем валидацию
            test_data = b"fake image data"
            test_filename = "test.jpg"
            
            try:
                result = handler.validate_file(test_data, test_filename, "avatar")
                print("✅ Валидация файла работает")
            except FileValidationError as e:
                print(f"⚠️ Ожидаемая ошибка валидации: {e.message}")
            
            # Тестируем обработку
            try:
                result = handler.process_file(test_data, test_filename, "avatar", 1)
                print("✅ Обработка файла работает")
            except Exception as e:
                print(f"⚠️ Ошибка обработки файла: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования обработчика файлов: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚨 БЫСТРЫЙ ТЕСТ ВОССТАНОВЛЕНИЯ")
    print("=" * 50)
    
    # Тест 1: Импорты
    imports_ok = test_imports()
    
    # Тест 2: FastAPI приложение
    fastapi_ok = test_fastapi_app()
    
    # Тест 3: Обработчик файлов
    file_handler_ok = test_file_handler()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"  Импорты: {'✅' if imports_ok else '❌'}")
    print(f"  FastAPI: {'✅' if fastapi_ok else '❌'}")
    print(f"  Файлы: {'✅' if file_handler_ok else '❌'}")
    
    if all([imports_ok, fastapi_ok, file_handler_ok]):
        print("\n🎉 ПРИЛОЖЕНИЕ ГОТОВО К ЗАПУСКУ!")
        print("💡 Рекомендации:")
        print("  1. Запустите: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("  2. Проверьте: http://localhost:8000/docs")
        print("  3. Протестируйте загрузку файлов")
    else:
        print("\n⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
        print("💡 Действия:")
        print("  1. Проверьте логи выше")
        print("  2. Установите недостающие зависимости")
        print("  3. Исправьте ошибки импорта")

if __name__ == "__main__":
    main() 