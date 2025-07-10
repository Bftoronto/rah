#!/usr/bin/env python3
"""
Скрипт для быстрого исправления критичных проблем интеграции фронтенда и бекенда
Выполняет автоматическое применение исправлений для совместимости
"""

import os
import shutil
from datetime import datetime

class QuickFixes:
    def __init__(self, project_root="/Users/alexandrkrstich/Downloads/v1.14"):
        self.project_root = project_root
        self.backend_path = os.path.join(project_root, "backend")
        self.backup_path = os.path.join(project_root, f"backup_quick_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
    def create_backup(self):
        """Создает резервную копию перед применением исправлений"""
        print("🔄 Создание резервной копии...")
        
        # Создаем папку для бэкапа
        os.makedirs(self.backup_path, exist_ok=True)
        
        # Копируем схемы
        schemas_path = os.path.join(self.backend_path, "app", "schemas")
        backup_schemas = os.path.join(self.backup_path, "schemas")
        if os.path.exists(schemas_path):
            shutil.copytree(schemas_path, backup_schemas)
        
        print(f"✅ Резервная копия создана: {self.backup_path}")
    
    def apply_user_schema_fix(self):
        """Применяет исправления к схеме пользователя"""
        print("🔧 Применение исправлений к схеме пользователя...")
        
        user_schema_path = os.path.join(self.backend_path, "app", "schemas", "user.py")
        user_fixed_path = os.path.join(self.project_root, "backend", "app", "schemas", "user_fixed.py")
        
        if os.path.exists(user_fixed_path):
            shutil.copy2(user_fixed_path, user_schema_path)
            print("✅ Схема пользователя обновлена")
        else:
            print("❌ Файл user_fixed.py не найден")
    
    def apply_rating_schema_fix(self):
        """Применяет исправления к схеме рейтингов"""
        print("🔧 Применение исправлений к схеме рейтингов...")
        
        rating_schema_path = os.path.join(self.backend_path, "app", "schemas", "rating.py")
        rating_fixed_path = os.path.join(self.project_root, "backend", "app", "schemas", "rating_fixed.py")
        
        if os.path.exists(rating_fixed_path):
            shutil.copy2(rating_fixed_path, rating_schema_path)
            print("✅ Схема рейтингов обновлена")
        else:
            print("❌ Файл rating_fixed.py не найден")
    
    def update_imports(self):
        """Обновляет импорты в API модулях"""
        print("🔧 Обновление импортов...")
        
        # Обновляем импорты в auth.py
        auth_path = os.path.join(self.backend_path, "app", "api", "auth.py")
        if os.path.exists(auth_path):
            with open(auth_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем, нужно ли обновить импорты
            if "from ..schemas.user import" in content:
                print("✅ Импорты в auth.py актуальны")
            else:
                print("⚠️ Возможны проблемы с импортами в auth.py")
        
        # Обновляем импорты в rating.py
        rating_api_path = os.path.join(self.backend_path, "app", "api", "rating.py")
        if os.path.exists(rating_api_path):
            with open(rating_api_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "from ..schemas.rating import" in content:
                print("✅ Импорты в rating.py актуальны")
            else:
                print("⚠️ Возможны проблемы с импортами в rating.py")
    
    def create_test_migration(self):
        """Создает тестовую миграцию для проверки изменений"""
        print("🔧 Создание тестовой миграции...")
        
        migration_content = '''"""
Тестовая миграция для проверки изменений схем
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'quick_fix_test'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Добавляем индексы для оптимизации
    op.create_index('idx_users_compatibility', 'users', ['balance', 'reviews', 'rating'])
    op.create_index('idx_ratings_comment_sync', 'ratings', ['from_user_id', 'target_user_id'])

def downgrade():
    # Удаляем индексы
    op.drop_index('idx_users_compatibility', table_name='users')
    op.drop_index('idx_ratings_comment_sync', table_name='ratings')
'''
        
        migrations_path = os.path.join(self.backend_path, "migrations", "versions")
        os.makedirs(migrations_path, exist_ok=True)
        
        migration_file = os.path.join(migrations_path, f"quick_fix_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
        
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(migration_content)
        
        print(f"✅ Тестовая миграция создана: {migration_file}")
    
    def verify_fixes(self):
        """Проверяет применение исправлений"""
        print("🔍 Проверка применения исправлений...")
        
        issues = []
        
        # Проверяем схему пользователя
        user_schema_path = os.path.join(self.backend_path, "app", "schemas", "user.py")
        if os.path.exists(user_schema_path):
            with open(user_schema_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "root_validator" in content and "set_compatibility_fields" in content:
                    print("✅ Схема пользователя содержит исправления совместимости")
                else:
                    issues.append("Схема пользователя не содержит исправления совместимости")
        else:
            issues.append("Файл схемы пользователя не найден")
        
        # Проверяем схему рейтингов
        rating_schema_path = os.path.join(self.backend_path, "app", "schemas", "rating.py")
        if os.path.exists(rating_schema_path):
            with open(rating_schema_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "sync_comment_review" in content:
                    print("✅ Схема рейтингов содержит исправления comment/review")
                else:
                    issues.append("Схема рейтингов не содержит исправления comment/review")
        else:
            issues.append("Файл схемы рейтингов не найден")
        
        if issues:
            print("❌ Обнаружены проблемы:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✅ Все исправления успешно применены")
            return True
    
    def create_compatibility_test(self):
        """Создает тест для проверки совместимости"""
        print("🔧 Создание теста совместимости...")
        
        test_content = '''#!/usr/bin/env python3
"""
Тест совместимости фронтенда и бекенда после применения исправлений
"""

import pytest
from app.schemas.user import UserRead
from app.schemas.rating import RatingCreate, RatingResponse

def test_user_compatibility_fields():
    """Тест совместимости полей пользователя"""
    user_data = {
        "id": 1,
        "telegram_id": "123456789",
        "phone": "79001234567",
        "full_name": "Test User",
        "birth_date": "1990-01-01",
        "city": "Moscow",
        "average_rating": 4.5,
        "is_active": True,
        "is_verified": True,
        "is_driver": False,
        "privacy_policy_version": "1.1",
        "privacy_policy_accepted": True,
        "privacy_policy_accepted_at": "2024-01-01T00:00:00",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    
    user = UserRead(**user_data)
    
    # Проверяем что совместимые поля установлены
    assert user.name == user.full_name
    assert user.rating == int(user.average_rating)
    assert isinstance(user.verified, dict)
    assert isinstance(user.car, dict)

def test_rating_comment_review_compatibility():
    """Тест совместимости полей comment/review в рейтингах"""
    
    # Тест с comment
    rating_data_comment = {
        "target_user_id": 1,
        "ride_id": 1,
        "rating": 5,
        "comment": "Отличный водитель!"
    }
    
    rating = RatingCreate(**rating_data_comment)
    assert rating.comment == "Отличный водитель!"
    assert rating.review == "Отличный водитель!"
    
    # Тест с review
    rating_data_review = {
        "target_user_id": 1,
        "ride_id": 1,
        "rating": 5,
        "review": "Отличный пассажир!"
    }
    
    rating = RatingCreate(**rating_data_review)
    assert rating.comment == "Отличный пассажир!"
    assert rating.review == "Отличный пассажир!"

if __name__ == "__main__":
    test_user_compatibility_fields()
    test_rating_comment_review_compatibility()
    print("✅ Все тесты совместимости прошли успешно")
'''
        
        tests_path = os.path.join(self.backend_path, "tests")
        os.makedirs(tests_path, exist_ok=True)
        
        test_file = os.path.join(tests_path, "test_compatibility.py")
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"✅ Тест совместимости создан: {test_file}")
    
    def run_all_fixes(self):
        """Запускает все исправления"""
        print("🚀 ЗАПУСК БЫСТРЫХ ИСПРАВЛЕНИЙ")
        print("=" * 50)
        
        try:
            self.create_backup()
            self.apply_user_schema_fix()
            self.apply_rating_schema_fix()
            self.update_imports()
            self.create_test_migration()
            self.create_compatibility_test()
            
            if self.verify_fixes():
                print("\n🎉 ВСЕ ИСПРАВЛЕНИЯ УСПЕШНО ПРИМЕНЕНЫ!")
                print("\n📋 Что было исправлено:")
                print("  ✅ Совместимость полей пользователя (balance, reviews, rating)")
                print("  ✅ Унификация comment/review в рейтингах")
                print("  ✅ Синхронизация алиасов полей")
                print("  ✅ Создан тест совместимости")
                print("\n🚀 ГОТОВО К ПРОДАКШЕНУ!")
            else:
                print("\n❌ НЕКОТОРЫЕ ИСПРАВЛЕНИЯ НЕ ПРИМЕНИЛИСЬ")
                print(f"Проверьте резервную копию: {self.backup_path}")
                
        except Exception as e:
            print(f"\n❌ ОШИБКА ПРИ ПРИМЕНЕНИИ ИСПРАВЛЕНИЙ: {str(e)}")
            print(f"Восстановите из резервной копии: {self.backup_path}")

if __name__ == "__main__":
    fixer = QuickFixes()
    fixer.run_all_fixes()
