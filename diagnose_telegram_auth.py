#!/usr/bin/env python3
"""
Диагностический скрипт для проверки авторизации Telegram Mini App
"""

import requests
import json
import time
from datetime import datetime

# URL'ы для тестирования
LOCAL_BACKEND = "http://localhost:8000"
PRODUCTION_BACKEND = "https://pax-backend-2gng.onrender.com"

def test_backend_connectivity(url, name):
    """Тест подключения к бэкенду"""
    print(f"\n🔧 Тестирование {name} ({url})...")
    
    try:
        # Тест корневого эндпоинта
        response = requests.get(f"{url}/", timeout=10)
        print(f"✅ {name} доступен (статус: {response.status_code})")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   Версия: {data.get('version', 'Неизвестна')}")
                print(f"   Статус: {data.get('status', 'Неизвестен')}")
            except:
                print("   Ответ не в формате JSON")
        
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ {name} недоступен (таймаут)")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} недоступен (ошибка подключения)")
        return False
    except Exception as e:
        print(f"❌ {name} недоступен: {e}")
        return False

def test_telegram_verification(url, name):
    """Тест верификации Telegram"""
    print(f"\n🤖 Тестирование верификации Telegram на {name}...")
    
    # Тестовые данные Telegram
    test_data = {
        "user": {
            "id": 123456789,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "language_code": "ru"
        },
        "auth_date": int(time.time()),
        "hash": "test_hash_for_development"
    }
    
    try:
        response = requests.post(
            f"{url}/api/auth/telegram/verify",
            json=test_data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code in [200, 401, 500]:
            print(f"✅ Эндпоинт верификации отвечает")
            try:
                data = response.json()
                print(f"Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
            except:
                print("Ответ не в формате JSON")
            return True
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования верификации: {e}")
        return False

def test_database_connection(url, name):
    """Тест подключения к базе данных"""
    print(f"\n🗄️ Тестирование подключения к БД на {name}...")
    
    try:
        response = requests.get(f"{url}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            db_status = data.get('database', 'unknown')
            print(f"✅ База данных: {db_status}")
            return db_status == 'connected'
        else:
            print(f"❌ Health check не пройден: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки БД: {e}")
        return False

def generate_test_telegram_data():
    """Генерация тестовых данных Telegram"""
    print("\n📱 Генерация тестовых данных Telegram...")
    
    # Симулируем данные Telegram Web App
    test_data = {
        "user": {
            "id": 123456789,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "language_code": "ru",
            "photo_url": "https://t.me/i/userpic/320/testuser.jpg"
        },
        "chat": {
            "id": -1001234567890,
            "type": "private",
            "title": "Test Chat"
        },
        "auth_date": int(time.time()),
        "hash": "test_hash_for_development_mode",
        "start_param": "test_start_param"
    }
    
    print("✅ Тестовые данные сгенерированы:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    return test_data

def main():
    """Основная функция диагностики"""
    print("🔍 ДИАГНОСТИКА TELEGRAM MINI APP АВТОРИЗАЦИИ")
    print("=" * 60)
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Тестируем подключение к бэкендам
    local_ok = test_backend_connectivity(LOCAL_BACKEND, "Локальный бэкенд")
    production_ok = test_backend_connectivity(PRODUCTION_BACKEND, "Продакшен бэкенд")
    
    # Выбираем рабочий бэкенд
    if local_ok:
        backend_url = LOCAL_BACKEND
        backend_name = "Локальный"
        print(f"\n✅ Используем локальный бэкенд: {backend_url}")
    elif production_ok:
        backend_url = PRODUCTION_BACKEND
        backend_name = "Продакшен"
        print(f"\n✅ Используем продакшен бэкенд: {backend_url}")
    else:
        print("\n❌ Нет доступных бэкендов!")
        print("Запустите локальный бэкенд: ./start_local_backend.sh")
        return
    
    # Тестируем базу данных
    db_ok = test_database_connection(backend_url, backend_name)
    
    # Тестируем верификацию Telegram
    auth_ok = test_telegram_verification(backend_url, backend_name)
    
    # Генерируем тестовые данные
    test_data = generate_test_telegram_data()
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    print(f"Бэкенд: {'✅ Работает' if local_ok or production_ok else '❌ Не работает'}")
    print(f"База данных: {'✅ Подключена' if db_ok else '❌ Не подключена'}")
    print(f"Верификация Telegram: {'✅ Работает' if auth_ok else '❌ Не работает'}")
    
    if local_ok or production_ok and auth_ok:
        print("\n🎉 Авторизация Telegram должна работать!")
        print("\n📱 Для тестирования:")
        print("1. Откройте бота @paxdemobot в Telegram")
        print("2. Нажмите кнопку 'Открыть приложение'")
        print("3. Приложение должно авторизовать вас автоматически")
    else:
        print("\n⚠️ Есть проблемы с авторизацией:")
        if not (local_ok or production_ok):
            print("- Бэкенд недоступен")
        if not db_ok:
            print("- Проблемы с базой данных")
        if not auth_ok:
            print("- Проблемы с верификацией Telegram")
        
        print("\n🔧 Рекомендации:")
        print("1. Запустите локальный бэкенд: ./start_local_backend.sh")
        print("2. Проверьте подключение к базе данных")
        print("3. Проверьте настройки Telegram бота")

if __name__ == "__main__":
    main() 