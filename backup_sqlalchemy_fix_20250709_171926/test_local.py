#!/usr/bin/env python3
"""
Временный тест для проверки исправлений импорта
"""

import sys
import os

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Тест импорта модулей"""
    try:
        # Тест импорта моделей
        from app.models import user, ride, chat, upload, notification, moderation, rating
        print("✅ Импорт моделей успешен")
        
        # Тест импорта database
        from app.database import init_db, check_db_connection
        print("✅ Импорт database успешен")
        
        # Тест импорта main
        from app.main import app
        print("✅ Импорт main успешен")
        
        print("\n🎉 ВСЕ ИМПОРТЫ РАБОТАЮТ КОРРЕКТНО!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Тестирование исправлений импорта...")
    success = test_imports()
    sys.exit(0 if success else 1) 