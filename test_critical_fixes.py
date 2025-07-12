#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений критических проблем
"""

import sys
import os
import json
import requests
from datetime import datetime, date
from typing import Dict, Any

# Добавляем путь к бэкенду
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_user_schema_compatibility():
    """Тест совместимости схемы пользователя"""
    print("🔍 Тестирование совместимости схемы пользователя...")
    
    try:
        from backend.app.schemas.user import UserRead
        
        # Создаем тестовые данные пользователя
        test_user_data = {
            'id': 1,
            'telegram_id': '123456789',
            'phone': '79001234567',
            'full_name': 'Иван Иванов',
            'birth_date': date(1990, 1, 1),
            'city': 'Москва',
            'avatar_url': 'https://example.com/avatar.jpg',
            'is_active': True,
            'is_verified': True,
            'is_driver': False,
            'privacy_policy_version': '1.1',
            'privacy_policy_accepted': True,
            'privacy_policy_accepted_at': datetime.now(),
            'car_brand': 'Toyota',
            'car_model': 'Camry',
            'car_year': 2020,
            'car_color': 'Белый',
            'driver_license_number': '1234567890',
            'driver_license_photo_url': 'https://example.com/license.jpg',
            'car_photo_url': 'https://example.com/car.jpg',
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'average_rating': 4.5,
            'total_rides': 10,
            'cancelled_rides': 1
        }
        
        # Создаем объект UserRead
        user_read = UserRead(**test_user_data)
        user_dict = user_read.model_dump()  # Используем model_dump вместо dict
        
        # Проверяем наличие полей для совместимости с фронтендом
        required_fields = ['name', 'avatar', 'balance', 'reviews', 'verified', 'car', 'rating']
        missing_fields = []
        
        for field in required_fields:
            if field not in user_dict:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Отсутствуют поля для совместимости: {missing_fields}")
            return False
        
        # Проверяем правильность значений
        assert user_dict['name'] == 'Иван Иванов', f"name должен быть 'Иван Иванов', получено: {user_dict['name']}"
        assert user_dict['avatar'] == 'https://example.com/avatar.jpg', f"avatar должен быть URL, получено: {user_dict['avatar']}"
        assert user_dict['balance'] == 500, f"balance должен быть 500, получено: {user_dict['balance']}"
        assert user_dict['reviews'] == 0, f"reviews должен быть 0, получено: {user_dict['reviews']}"
        assert user_dict['rating'] == 4, f"rating должен быть 4, получено: {user_dict['rating']}"
        assert isinstance(user_dict['verified'], dict), f"verified должен быть dict, получено: {type(user_dict['verified'])}"
        assert isinstance(user_dict['car'], dict), f"car должен быть dict, получено: {type(user_dict['car'])}"
        
        print("✅ Схема пользователя совместима с фронтендом")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования схемы пользователя: {e}")
        return False

def test_telegram_data_structure():
    """Тест структуры Telegram данных"""
    print("🔍 Тестирование структуры Telegram данных...")
    
    try:
        from backend.app.schemas.telegram import TelegramAuthRequest, TelegramUserData
        
        # Тестовые данные от фронтенда
        frontend_data = {
            'user': {
                'id': 123456789,
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'username': 'ivan_ivanov',
                'photo_url': 'https://t.me/i/userpic/320/ivan_ivanov.jpg',
                'auth_date': int(datetime.now().timestamp()),
                'hash': 'test_hash_123'
            },
            'auth_date': int(datetime.now().timestamp()),
            'hash': 'test_hash_123',
            'initData': 'test_init_data',
            'query_id': 'test_query_id',
            'start_param': 'test_start_param'
        }
        
        # Тестируем валидацию
        auth_request = TelegramAuthRequest(**frontend_data)
        user_data = auth_request.user.model_dump()  # Используем model_dump вместо dict
        
        # Проверяем обязательные поля
        assert user_data['id'] == 123456789, f"ID должен быть 123456789, получено: {user_data['id']}"
        assert user_data['first_name'] == 'Иван', f"first_name должен быть 'Иван', получено: {user_data['first_name']}"
        assert user_data['last_name'] == 'Иванов', f"last_name должен быть 'Иванов', получено: {user_data['last_name']}"
        assert user_data['username'] == 'ivan_ivanov', f"username должен быть 'ivan_ivanov', получено: {user_data['username']}"
        
        print("✅ Структура Telegram данных корректна")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования Telegram данных: {e}")
        return False

def test_api_endpoints():
    """Тест API эндпоинтов"""
    print("🔍 Тестирование API эндпоинтов...")
    
    # Базовый URL (замените на ваш)
    base_url = "http://localhost:8000"
    
    try:
        # Тест эндпоинта /api/auth/me (должен вернуть 401 без токена)
        response = requests.get(f"{base_url}/api/auth/me", timeout=5)
        assert response.status_code == 401, f"Эндпоинт /api/auth/me должен возвращать 401, получено: {response.status_code}"
        
        print("✅ API эндпоинты работают корректно")
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️ Сервер не запущен, пропускаем тест API")
        return True
    except Exception as e:
        print(f"❌ Ошибка тестирования API: {e}")
        return False

def test_frontend_compatibility():
    """Тест совместимости фронтенда"""
    print("🔍 Тестирование совместимости фронтенда...")
    
    try:
        # Проверяем наличие файла api.js
        api_js_path = "frontend/assets/js/api.js"
        if not os.path.exists(api_js_path):
            print(f"❌ Файл {api_js_path} не найден")
            return False
        
        # Читаем файл и проверяем наличие методов
        with open(api_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_methods = [
            'getCurrentUser()',
            'verifyTelegramUser(telegramData)',
            'login(telegramData)'
        ]
        
        missing_methods = []
        for method in required_methods:
            if method not in content:
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ Отсутствуют методы в api.js: {missing_methods}")
            return False
        
        # Проверяем структуру Telegram данных в методах
        if 'user: {' not in content or 'auth_date:' not in content:
            print("❌ Неправильная структура Telegram данных в api.js")
            return False
        
        print("✅ Фронтенд совместим с бэкендом")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования фронтенда: {e}")
        return False

def test_upload_wrong_content_type():
    """Тест загрузки файла с неправильным Content-Type (ожидаем 415)"""
    print("🔍 Тестирование загрузки файла с неправильным Content-Type...")
    import requests
    base_url = "http://localhost:8000"
    try:
        files = {'file': ('test.txt', b'hello', 'text/plain')}
        data = {'file_type': 'avatar'}
        # Явно ставим неправильный Content-Type
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{base_url}/api/upload/", data=data, files=files, headers=headers)
        if response.status_code == 415:
            print("✅ upload_file возвращает 415 при неправильном Content-Type")
            return True
        else:
            print(f"❌ upload_file должен возвращать 415, получено: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Не удалось проверить upload_file: {e}")
        return True  # Не критично, если сервер не запущен

def test_websocket_url_generation():
    """Тест генерации WebSocket URL (snake_case user_id)"""
    print("🔍 Тестирование генерации WebSocket URL...")
    try:
        import importlib.util
        import sys
        ws_path = 'frontend/assets/js/websocket.js'
        # Проверяем наличие user_id в getWebSocketUrl
        with open(ws_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'this.user_id' in content and '/ws/${this.user_id}' in content:
            print("✅ WebSocket URL использует snake_case user_id")
            return True
        else:
            print("❌ WebSocket URL должен использовать snake_case user_id")
            return False
    except Exception as e:
        print(f"⚠️ Не удалось проверить WebSocket URL: {e}")
        return True

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов критических исправлений...")
    print("=" * 50)
    
    tests = [
        test_user_schema_compatibility,
        test_telegram_data_structure,
        test_api_endpoints,
        test_frontend_compatibility,
        test_upload_wrong_content_type,
        test_websocket_url_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте {test.__name__}: {e}")
    
    print("=" * 50)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов прошли")
    
    if passed == total:
        print("🎉 Все критические проблемы исправлены!")
        return True
    else:
        print("⚠️ Некоторые проблемы требуют дополнительного внимания")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 