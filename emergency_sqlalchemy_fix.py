#!/usr/bin/env python3
"""
ЭКСТРЕННЫЙ СКРИПТ ВОССТАНОВЛЕНИЯ SQLALCHEMY ИМПОРТОВ
Критическое исправление для запуска приложения
"""

import os
import sys
import subprocess
import re
from pathlib import Path

def log(message):
    """Логирование с временными метками"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_sqlalchemy_version():
    """Проверка версии SQLAlchemy"""
    try:
        import sqlalchemy
        log(f"SQLAlchemy версия: {sqlalchemy.__version__}")
        return sqlalchemy.__version__
    except ImportError as e:
        log(f"ОШИБКА: SQLAlchemy не установлен: {e}")
        return None

def fix_sqlalchemy_imports():
    """Исправление импортов SQLAlchemy"""
    backend_dir = Path("backend/app")
    
    # Паттерны для поиска и замены
    import_fixes = [
        # selectinload
        (r"from sqlalchemy import selectinload", "from sqlalchemy.orm import selectinload"),
        (r"from sqlalchemy import.*selectinload", "from sqlalchemy.orm import selectinload"),
        
        # joinedload
        (r"from sqlalchemy import joinedload", "from sqlalchemy.orm import joinedload"),
        (r"from sqlalchemy import.*joinedload", "from sqlalchemy.orm import joinedload"),
        
        # subqueryload
        (r"from sqlalchemy import subqueryload", "from sqlalchemy.orm import subqueryload"),
        (r"from sqlalchemy import.*subqueryload", "from sqlalchemy.orm import subqueryload"),
        
        # lazyload
        (r"from sqlalchemy import lazyload", "from sqlalchemy.orm import lazyload"),
        (r"from sqlalchemy import.*lazyload", "from sqlalchemy.orm import lazyload"),
        
        # immediateload
        (r"from sqlalchemy import immediateload", "from sqlalchemy.orm import immediateload"),
        (r"from sqlalchemy import.*immediateload", "from sqlalchemy.orm import immediateload"),
        
        # noload
        (r"from sqlalchemy import noload", "from sqlalchemy.orm import noload"),
        (r"from sqlalchemy import.*noload", "from sqlalchemy.orm import noload"),
        
        # contains_eager
        (r"from sqlalchemy import contains_eager", "from sqlalchemy.orm import contains_eager"),
        (r"from sqlalchemy import.*contains_eager", "from sqlalchemy.orm import contains_eager"),
        
        # defer
        (r"from sqlalchemy import defer", "from sqlalchemy.orm import defer"),
        (r"from sqlalchemy import.*defer", "from sqlalchemy.orm import defer"),
        
        # undefer
        (r"from sqlalchemy import undefer", "from sqlalchemy.orm import undefer"),
        (r"from sqlalchemy import.*undefer", "from sqlalchemy.orm import undefer"),
        
        # undefer_group
        (r"from sqlalchemy import undefer_group", "from sqlalchemy.orm import undefer_group"),
        (r"from sqlalchemy import.*undefer_group", "from sqlalchemy.orm import undefer_group"),
        
        # with_expression
        (r"from sqlalchemy import with_expression", "from sqlalchemy.orm import with_expression"),
        (r"from sqlalchemy import.*with_expression", "from sqlalchemy.orm import with_expression"),
    ]
    
    fixed_files = []
    
    for py_file in backend_dir.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modified = False
            
            for pattern, replacement in import_fixes:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    modified = True
                    log(f"Исправлен импорт в {py_file}")
            
            if modified:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(str(py_file))
                
        except Exception as e:
            log(f"ОШИБКА при обработке {py_file}: {e}")
    
    return fixed_files

def test_imports():
    """Тестирование критических импортов"""
    critical_modules = [
        "app.main",
        "app.services.auth_service",
        "app.services.ride_service",
        "app.api.auth",
        "app.api.rides"
    ]
    
    failed_imports = []
    
    for module in critical_modules:
        try:
            __import__(module)
            log(f"✅ {module} - импорт успешен")
        except ImportError as e:
            log(f"❌ {module} - ОШИБКА ИМПОРТА: {e}")
            failed_imports.append((module, str(e)))
        except Exception as e:
            log(f"❌ {module} - НЕОЖИДАННАЯ ОШИБКА: {e}")
            failed_imports.append((module, str(e)))
    
    return failed_imports

def create_backup():
    """Создание резервной копии"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_sqlalchemy_fix_{timestamp}"
    
    try:
        shutil.copytree("backend", backup_dir)
        log(f"✅ Резервная копия создана: {backup_dir}")
        return backup_dir
    except Exception as e:
        log(f"❌ ОШИБКА создания резервной копии: {e}")
        return None

def main():
    """Основная функция экстренного восстановления"""
    log("🚨 ЗАПУСК ЭКСТРЕННОГО ВОССТАНОВЛЕНИЯ SQLALCHEMY")
    
    # 1. Проверка версии SQLAlchemy
    log("1. Проверка версии SQLAlchemy...")
    version = check_sqlalchemy_version()
    if not version:
        log("❌ КРИТИЧЕСКАЯ ОШИБКА: SQLAlchemy не установлен")
        return False
    
    # 2. Создание резервной копии
    log("2. Создание резервной копии...")
    backup_dir = create_backup()
    
    # 3. Исправление импортов
    log("3. Исправление импортов SQLAlchemy...")
    fixed_files = fix_sqlalchemy_imports()
    log(f"✅ Исправлено файлов: {len(fixed_files)}")
    
    # 4. Тестирование импортов
    log("4. Тестирование критических импортов...")
    failed_imports = test_imports()
    
    if failed_imports:
        log("❌ КРИТИЧЕСКИЕ ОШИБКИ ИМПОРТА:")
        for module, error in failed_imports:
            log(f"   {module}: {error}")
        return False
    else:
        log("✅ ВСЕ КРИТИЧЕСКИЕ ИМПОРТЫ УСПЕШНЫ")
    
    # 5. Финальная проверка
    log("5. Финальная проверка приложения...")
    try:
        import app.main
        log("✅ ПРИЛОЖЕНИЕ ГОТОВО К ЗАПУСКУ")
        return True
    except Exception as e:
        log(f"❌ ФИНАЛЬНАЯ ОШИБКА: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        log("🎉 ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО УСПЕШНО")
        sys.exit(0)
    else:
        log("💥 ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ ЗАВЕРШЕНО С ОШИБКАМИ")
        sys.exit(1) 