#!/usr/bin/env python3
"""
Скрипт для проверки статуса фронтенда и бэкенда
"""

import requests
import json
from datetime import datetime

# URL'ы для проверки
FRONTEND_URL = "https://frabjous-florentine-c506b0.netlify.app"
BACKEND_URL = "https://pax-backend-2gng.onrender.com"

def check_frontend():
    """Проверка доступности фронтенда"""
    print("🌐 Проверка фронтенда...")
    print(f"URL: {FRONTEND_URL}")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        
        if response.status_code == 200:
            print("✅ Фронтенд доступен")
            print(f"Статус: {response.status_code}")
            print(f"Размер ответа: {len(response.content)} байт")
            
            # Проверяем наличие ключевых элементов
            content = response.text
            if "PAX" in content:
                print("✅ Название приложения найдено")
            if "Telegram" in content:
                print("✅ Telegram интеграция найдена")
            if "assets/js" in content:
                print("✅ JavaScript файлы найдены")
                
            return True
        else:
            print(f"❌ Фронтенд недоступен. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к фронтенду: {e}")
        return False

def check_backend():
    """Проверка доступности бэкенда"""
    print("\n🔧 Проверка бэкенда...")
    print(f"URL: {BACKEND_URL}")
    
    try:
        # Проверяем корневой эндпоинт
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Бэкенд доступен")
            print(f"Статус: {response.status_code}")
            
            try:
                data = response.json()
                print(f"Версия: {data.get('version', 'Неизвестна')}")
                print(f"Статус: {data.get('status', 'Неизвестен')}")
            except:
                print("Ответ не в формате JSON")
                
            return True
        else:
            print(f"❌ Бэкенд недоступен. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к бэкенду: {e}")
        return False

def check_backend_health():
    """Проверка здоровья бэкенда"""
    print("\n🏥 Проверка здоровья бэкенда...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check пройден")
            print(f"Статус: {data.get('status', 'Неизвестен')}")
            print(f"База данных: {data.get('database', 'Неизвестна')}")
            print(f"Версия: {data.get('version', 'Неизвестна')}")
            return True
        else:
            print(f"❌ Health check не пройден. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка health check: {e}")
        return False

def check_api_info():
    """Проверка информации об API"""
    print("\n📋 Проверка информации об API...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/info", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API информация получена")
            print(f"Название: {data.get('name', 'Неизвестно')}")
            print(f"Версия: {data.get('version', 'Неизвестна')}")
            print(f"Debug режим: {data.get('debug', 'Неизвестен')}")
            
            endpoints = data.get('endpoints', {})
            print("Доступные эндпоинты:")
            for name, path in endpoints.items():
                print(f"  - {name}: {path}")
                
            return True
        else:
            print(f"❌ Не удалось получить информацию об API. Статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка получения информации об API: {e}")
        return False

def test_telegram_verification():
    """Тест верификации Telegram (без реальных данных)"""
    print("\n🤖 Тест эндпоинта верификации Telegram...")
    
    try:
        # Отправляем тестовые данные
        test_data = {
            "id": 123456789,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "auth_date": int(datetime.now().timestamp()),
            "hash": "test_hash"
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/auth/telegram/verify",
            json=test_data,
            timeout=10
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        if response.status_code in [200, 401, 500]:
            print("✅ Эндпоинт верификации Telegram отвечает")
            try:
                data = response.json()
                print(f"Ответ: {data}")
            except:
                print("Ответ не в формате JSON")
            return True
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования верификации: {e}")
        return False

def main():
    """Основная функция"""
    print("🔍 Проверка статуса приложения...")
    print("=" * 60)
    
    # Проверяем фронтенд
    frontend_ok = check_frontend()
    
    # Проверяем бэкенд
    backend_ok = check_backend()
    
    if backend_ok:
        # Проверяем здоровье бэкенда
        check_backend_health()
        
        # Проверяем информацию об API
        check_api_info()
        
        # Тестируем верификацию Telegram
        test_telegram_verification()
    
    print("\n" + "=" * 60)
    print("📊 Итоговый статус:")
    print(f"Фронтенд: {'✅ Работает' if frontend_ok else '❌ Не работает'}")
    print(f"Бэкенд: {'✅ Работает' if backend_ok else '❌ Не работает'}")
    
    if frontend_ok and backend_ok:
        print("\n🎉 Все системы работают! Telegram Mini App должен функционировать.")
        print("\n📱 Для тестирования:")
        print("1. Откройте бота @paxdemobot в Telegram")
        print("2. Нажмите кнопку 'Открыть приложение'")
        print("3. Приложение должно открыться и авторизовать вас")
    else:
        print("\n⚠️ Есть проблемы с доступностью. Проверьте настройки.")

if __name__ == "__main__":
    main() 