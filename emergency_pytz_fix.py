#!/usr/bin/env python3
"""
ЭКСТРЕННЫЙ СКРИПТ ВОССТАНОВЛЕНИЯ
Исправление критической ошибки ModuleNotFoundError: No module named 'pytz'
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Выполнение команды с логированием"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - УСПЕШНО")
            return True
        else:
            print(f"❌ {description} - ОШИБКА:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} - ИСКЛЮЧЕНИЕ: {e}")
        return False

def emergency_fix():
    """Экстренное исправление проблемы с pytz"""
    print("🚨 ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ СИСТЕМЫ")
    print("=" * 50)
    
    # 1. Проверка текущего состояния
    print("📋 Проверка текущего состояния...")
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Директория backend не найдена!")
        return False
    
    # 2. Установка pytz
    print("\n📦 Установка зависимостей...")
    if not run_command("cd backend && pip install pytz==2023.3", "Установка pytz"):
        print("⚠️  Попытка альтернативной установки...")
        if not run_command("pip install pytz==2023.3", "Альтернативная установка pytz"):
            return False
    
    # 3. Обновление requirements.txt
    print("\n📝 Обновление requirements.txt...")
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, "r") as f:
            content = f.read()
        
        if "pytz" not in content:
            with open(requirements_file, "a") as f:
                f.write("\npytz==2023.3\n")
            print("✅ pytz добавлен в requirements.txt")
        else:
            print("✅ pytz уже присутствует в requirements.txt")
    
    # 4. Проверка исправления
    print("\n🔍 Проверка исправления...")
    test_script = """
import sys
sys.path.append('backend')
try:
    from app.config.settings import get_settings
    settings = get_settings()
    print("✅ Настройки загружены успешно")
    print(f"Timezone: {settings.timezone}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
"""
    
    with open("test_fix.py", "w") as f:
        f.write(test_script)
    
    if run_command("python test_fix.py", "Тестирование исправления"):
        print("✅ Проблема исправлена!")
        os.remove("test_fix.py")
        return True
    else:
        print("❌ Проблема не исправлена")
        return False

def alternative_fix():
    """Альтернативное исправление без pytz"""
    print("\n🔄 АЛЬТЕРНАТИВНОЕ ИСПРАВЛЕНИЕ (без pytz)")
    print("=" * 50)
    
    # Замена pytz на zoneinfo
    settings_file = Path("backend/app/config/settings.py")
    if settings_file.exists():
        with open(settings_file, "r") as f:
            content = f.read()
        
        # Замена импорта и использования
        content = content.replace("import pytz", "import zoneinfo")
        content = content.replace("pytz.timezone(v)", "zoneinfo.ZoneInfo(v)")
        content = content.replace("pytz.exceptions.UnknownTimeZoneError", "zoneinfo.ZoneInfoNoKeyError")
        
        with open(settings_file, "w") as f:
            f.write(content)
        
        print("✅ Заменен pytz на zoneinfo")
        return True
    else:
        print("❌ Файл settings.py не найден")
        return False

if __name__ == "__main__":
    print("🚨 ЭКСТРЕННОЕ ВОССТАНОВЛЕНИЕ ПРИЛОЖЕНИЯ")
    print("Проблема: ModuleNotFoundError: No module named 'pytz'")
    print("=" * 60)
    
    # Попытка основного исправления
    if emergency_fix():
        print("\n🎉 СИСТЕМА ВОССТАНОВЛЕНА!")
        print("✅ Приложение готово к запуску")
    else:
        print("\n⚠️  Основное исправление не удалось")
        # Попытка альтернативного исправления
        if alternative_fix():
            print("✅ Альтернативное исправление применено")
            print("🔄 Перезапустите приложение")
        else:
            print("❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось исправить")
            sys.exit(1) 