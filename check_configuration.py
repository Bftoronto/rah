#!/usr/bin/env python3
"""
Скрипт для проверки соответствия конфигурации указанным данным
"""

import requests
import json
import re
from datetime import datetime

# Ожидаемые значения
EXPECTED_CONFIG = {
    "database_url": "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain",
    "database_password": "IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN",
    "backend_url": "https://pax-backend-2gng.onrender.com",
    "frontend_url": "https://frabjous-florentine-c506b0.netlify.app",
    "telegram_bot_token": "8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA"
}

def check_file_configuration():
    """Проверка конфигурации в файлах"""
    print("🔍 Проверка конфигурации в файлах...")
    
    issues = []
    
    # Проверка backend/app/config_simple.py
    try:
        with open('backend/app/config_simple.py', 'r') as f:
            content = f.read()
            
        if EXPECTED_CONFIG["database_url"] not in content:
            issues.append("❌ backend/app/config_simple.py: Неправильный DATABASE_URL")
        else:
            print("✅ backend/app/config_simple.py: DATABASE_URL корректный")
            
        if EXPECTED_CONFIG["telegram_bot_token"] not in content:
            issues.append("❌ backend/app/config_simple.py: Неправильный TELEGRAM_BOT_TOKEN")
        else:
            print("✅ backend/app/config_simple.py: TELEGRAM_BOT_TOKEN корректный")
            
    except FileNotFoundError:
        issues.append("❌ backend/app/config_simple.py: Файл не найден")
    
    # Проверка backend/docker-compose.yml
    try:
        with open('backend/docker-compose.yml', 'r') as f:
            content = f.read()
            
        if EXPECTED_CONFIG["database_url"] not in content:
            issues.append("❌ backend/docker-compose.yml: Неправильный DATABASE_URL")
        else:
            print("✅ backend/docker-compose.yml: DATABASE_URL корректный")
            
    except FileNotFoundError:
        issues.append("❌ backend/docker-compose.yml: Файл не найден")
    
    # Проверка backend/alembic.ini
    try:
        with open('backend/alembic.ini', 'r') as f:
            content = f.read()
            
        if EXPECTED_CONFIG["database_url"] not in content:
            issues.append("❌ backend/alembic.ini: Неправильный sqlalchemy.url")
        else:
            print("✅ backend/alembic.ini: sqlalchemy.url корректный")
            
    except FileNotFoundError:
        issues.append("❌ backend/alembic.ini: Файл не найден")
    
    # Проверка assets/js/api.js
    try:
        with open('assets/js/api.js', 'r') as f:
            content = f.read()
            
        if EXPECTED_CONFIG["backend_url"] not in content:
            issues.append("❌ assets/js/api.js: Неправильный backend URL")
        else:
            print("✅ assets/js/api.js: Backend URL корректный")
            
        # Проверяем наличие домена в проверке окружения
        if "frabjous-florentine-c506b0.netlify.app" not in content:
            issues.append("❌ assets/js/api.js: Неправильный frontend URL")
        else:
            print("✅ assets/js/api.js: Frontend URL корректный")
            
    except FileNotFoundError:
        issues.append("❌ assets/js/api.js: Файл не найден")
    
    return issues

def check_backend_connectivity():
    """Проверка доступности бэкенда"""
    print("\n🌐 Проверка доступности бэкенда...")
    
    try:
        response = requests.get(f"{EXPECTED_CONFIG['backend_url']}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Бэкенд доступен")
            print(f"   Статус: {data.get('status', 'Неизвестен')}")
            print(f"   База данных: {data.get('database', 'Неизвестна')}")
            print(f"   Версия: {data.get('version', 'Неизвестна')}")
            return True
        else:
            print(f"❌ Бэкенд недоступен. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к бэкенду: {e}")
        return False

def check_frontend_connectivity():
    """Проверка доступности фронтенда"""
    print("\n🌐 Проверка доступности фронтенда...")
    
    try:
        response = requests.get(EXPECTED_CONFIG["frontend_url"], timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Фронтенд доступен")
            print(f"   Статус: {response.status_code}")
            return True
        else:
            print(f"❌ Фронтенд недоступен. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к фронтенду: {e}")
        return False

def check_database_connection():
    """Проверка подключения к базе данных через API"""
    print("\n🗄️ Проверка подключения к базе данных...")
    
    try:
        response = requests.get(f"{EXPECTED_CONFIG['backend_url']}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            db_status = data.get('database', 'unknown')
            
            if db_status == 'connected':
                print("✅ Подключение к базе данных работает")
                return True
            else:
                print(f"❌ Проблемы с подключением к БД: {db_status}")
                return False
        else:
            print(f"❌ Не удалось проверить БД. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")
        return False

def check_telegram_bot():
    """Проверка Telegram бота"""
    print("\n🤖 Проверка Telegram бота...")
    
    try:
        bot_token = EXPECTED_CONFIG["telegram_bot_token"]
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Telegram бот активен")
                print(f"   Имя: {bot_info.get('first_name', 'Неизвестно')}")
                print(f"   Username: @{bot_info.get('username', 'Неизвестно')}")
                print(f"   ID: {bot_info.get('id', 'Неизвестно')}")
                return True
            else:
                print(f"❌ Telegram бот неактивен: {data.get('description', 'Неизвестная ошибка')}")
                return False
        else:
            print(f"❌ Ошибка проверки Telegram бота. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки Telegram бота: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🔍 ПРОВЕРКА КОНФИГУРАЦИИ ПРОЕКТА")
    print("=" * 50)
    print(f"Дата проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Проверка конфигурации в файлах
    file_issues = check_file_configuration()
    
    # Проверка доступности сервисов
    backend_ok = check_backend_connectivity()
    frontend_ok = check_frontend_connectivity()
    database_ok = check_database_connection()
    telegram_ok = check_telegram_bot()
    
    # Вывод результатов
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("=" * 50)
    
    if file_issues:
        print("\n❌ ПРОБЛЕМЫ В КОНФИГУРАЦИИ:")
        for issue in file_issues:
            print(f"   {issue}")
    else:
        print("\n✅ КОНФИГУРАЦИЯ КОРРЕКТНА")
    
    print(f"\n🌐 СЕРВИСЫ:")
    print(f"   Бэкенд: {'✅ Доступен' if backend_ok else '❌ Недоступен'}")
    print(f"   Фронтенд: {'✅ Доступен' if frontend_ok else '❌ Недоступен'}")
    print(f"   База данных: {'✅ Доступна' if database_ok else '❌ Недоступна'}")
    print(f"   Telegram бот: {'✅ Активен' if telegram_ok else '❌ Неактивен'}")
    
    # Общая оценка
    all_ok = not file_issues and backend_ok and frontend_ok and database_ok and telegram_ok
    
    print(f"\n🎯 ОБЩАЯ ОЦЕНКА: {'✅ ВСЕ ОК' if all_ok else '❌ ЕСТЬ ПРОБЛЕМЫ'}")
    
    if not all_ok:
        print("\n💡 РЕКОМЕНДАЦИИ:")
        if file_issues:
            print("   - Исправьте проблемы в конфигурационных файлах")
        if not backend_ok:
            print("   - Проверьте доступность бэкенда")
        if not frontend_ok:
            print("   - Проверьте доступность фронтенда")
        if not database_ok:
            print("   - Проверьте подключение к базе данных")
        if not telegram_ok:
            print("   - Проверьте настройки Telegram бота")

if __name__ == "__main__":
    main() 