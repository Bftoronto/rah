#!/usr/bin/env python3
"""
ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С AIOHTTP
Скрипт для немедленного устранения ошибки ModuleNotFoundError: No module named 'aiohttp'
"""

import subprocess
import sys
import os
import requests
import json
from datetime import datetime

def log(message):
    """Логирование с временной меткой"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_python_version():
    """Проверка версии Python"""
    version = sys.version_info
    log(f"Python версия: {version.major}.{version.minor}.{version.micro}")
    return version

def install_aiohttp():
    """Установка aiohttp"""
    try:
        log("Устанавливаю aiohttp...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "aiohttp==3.9.1"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            log("✅ aiohttp успешно установлен")
            return True
        else:
            log(f"❌ Ошибка установки aiohttp: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ Критическая ошибка при установке aiohttp: {e}")
        return False

def verify_aiohttp_installation():
    """Проверка установки aiohttp"""
    try:
        import aiohttp
        log(f"✅ aiohttp импортирован успешно, версия: {aiohttp.__version__}")
        return True
    except ImportError as e:
        log(f"❌ aiohttp не установлен: {e}")
        return False

def check_backend_health():
    """Проверка здоровья бэкенда"""
    try:
        url = "https://pax-backend-2gng.onrender.com/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Бэкенд работает: {data}")
            return True
        else:
            log(f"❌ Бэкенд недоступен: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Ошибка проверки бэкенда: {e}")
        return False

def check_database_connection():
    """Проверка подключения к базе данных"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Парсинг URL базы данных
        db_url = "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain"
        parsed = urlparse(db_url)
        
        # Подключение к базе данных
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        log("✅ Подключение к базе данных успешно")
        return True
        
    except Exception as e:
        log(f"❌ Ошибка подключения к базе данных: {e}")
        return False

def check_telegram_bot():
    """Проверка Telegram бота"""
    try:
        bot_token = "8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA"
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data["result"]
                log(f"✅ Telegram бот работает: @{bot_info['username']}")
                return True
            else:
                log(f"❌ Ошибка Telegram API: {data}")
                return False
        else:
            log(f"❌ Telegram бот недоступен: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ Ошибка проверки Telegram бота: {e}")
        return False

def check_frontend():
    """Проверка фронтенда"""
    try:
        url = "https://frabjous-florentine-c506b0.netlify.app"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            log("✅ Фронтенд доступен")
            return True
        else:
            log(f"❌ Фронтенд недоступен: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ Ошибка проверки фронтенда: {e}")
        return False

def update_requirements():
    """Обновление requirements.txt"""
    try:
        requirements_path = "backend/requirements.txt"
        
        # Проверяем, есть ли aiohttp в requirements
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        if 'aiohttp' not in content:
            log("Добавляю aiohttp в requirements.txt...")
            with open(requirements_path, 'a') as f:
                f.write("aiohttp==3.9.1\n")
            log("✅ requirements.txt обновлен")
        else:
            log("✅ aiohttp уже есть в requirements.txt")
        
        return True
        
    except Exception as e:
        log(f"❌ Ошибка обновления requirements.txt: {e}")
        return False

def main():
    """Основная функция исправления"""
    log("🚨 ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С AIOHTTP")
    log("=" * 60)
    
    # 1. Проверка версии Python
    check_python_version()
    
    # 2. Установка aiohttp
    if not install_aiohttp():
        log("❌ КРИТИЧЕСКАЯ ОШИБКА: Не удалось установить aiohttp")
        return False
    
    # 3. Проверка установки
    if not verify_aiohttp_installation():
        log("❌ КРИТИЧЕСКАЯ ОШИБКА: aiohttp не установлен")
        return False
    
    # 4. Обновление requirements.txt
    update_requirements()
    
    # 5. Проверка компонентов системы
    log("\n🔍 ПРОВЕРКА КОМПОНЕНТОВ СИСТЕМЫ")
    log("-" * 40)
    
    backend_ok = check_backend_health()
    db_ok = check_database_connection()
    bot_ok = check_telegram_bot()
    frontend_ok = check_frontend()
    
    # 6. Итоговый отчет
    log("\n📊 ИТОГОВЫЙ ОТЧЕТ")
    log("-" * 40)
    log(f"✅ aiohttp: УСТАНОВЛЕН")
    log(f"{'✅' if backend_ok else '❌'} Бэкенд: {'РАБОТАЕТ' if backend_ok else 'НЕ РАБОТАЕТ'}")
    log(f"{'✅' if db_ok else '❌'} База данных: {'ПОДКЛЮЧЕНА' if db_ok else 'НЕ ПОДКЛЮЧЕНА'}")
    log(f"{'✅' if bot_ok else '❌'} Telegram бот: {'РАБОТАЕТ' if bot_ok else 'НЕ РАБОТАЕТ'}")
    log(f"{'✅' if frontend_ok else '❌'} Фронтенд: {'ДОСТУПЕН' if frontend_ok else 'НЕ ДОСТУПЕН'}")
    
    # 7. Рекомендации
    log("\n💡 РЕКОМЕНДАЦИИ")
    log("-" * 40)
    
    if not backend_ok:
        log("🔧 Перезапустите бэкенд на Render")
        log("   - Зайдите в Render Dashboard")
        log("   - Найдите сервис pax-backend-2gng")
        log("   - Нажмите 'Manual Deploy'")
    
    if not db_ok:
        log("🔧 Проверьте подключение к базе данных")
        log("   - Убедитесь, что база данных активна")
        log("   - Проверьте правильность URL")
    
    if not bot_ok:
        log("🔧 Проверьте настройки Telegram бота")
        log("   - Убедитесь, что токен правильный")
        log("   - Проверьте, что бот не заблокирован")
    
    if not frontend_ok:
        log("🔧 Проверьте развертывание фронтенда")
        log("   - Убедитесь, что Netlify работает")
        log("   - Проверьте настройки домена")
    
    # 8. Успешное завершение
    if backend_ok and db_ok and bot_ok and frontend_ok:
        log("\n🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ!")
        log("✅ Готово к презентации инвестору")
        return True
    else:
        log("\n⚠️ ЕСТЬ ПРОБЛЕМЫ, ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 