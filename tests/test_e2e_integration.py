"""
E2E тесты интеграции для проверки полного цикла работы приложения
Проверяет взаимодействие между фронтендом и бэкендом
"""

import pytest
import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch
import os
import sys

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.app.main import app
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.ride import Ride
from backend.app.models.rating import Rating
from backend.app.schemas.user import UserCreate
from backend.app.schemas.ride import RideCreate
from backend.app.schemas.rating import RatingCreate

class E2EIntegrationTest:
    """Класс для E2E тестов интеграции"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_user_data = {
            "telegram_id": "123456789",
            "username": "test_user",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+79001234567",
            "email": "test@example.com"
        }
        self.test_ride_data = {
            "from_location": "Москва",
            "to_location": "Санкт-Петербург",
            "departure_time": "2024-01-15T10:00:00",
            "seats_available": 3,
            "price": 1500,
            "description": "Тестовая поездка"
        }
        self.session = None
        self.access_token = None
        
    async def setup(self):
        """Настройка тестового окружения"""
        self.session = aiohttp.ClientSession()
        
    async def teardown(self):
        """Очистка тестового окружения"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                          headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Выполнение HTTP запроса"""
        url = f"{self.base_url}{endpoint}"
        
        if headers is None:
            headers = {}
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        headers["Content-Type"] = "application/json"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    return await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data, headers=headers) as response:
                    return await response.json()
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data, headers=headers) as response:
                    return await response.json()
            elif method.upper() == "DELETE":
                async with self.session.delete(url, headers=headers) as response:
                    return await response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def test_user_registration_flow(self):
        """Тест полного цикла регистрации пользователя"""
        print("🧪 Тестирование регистрации пользователя...")
        
        # 1. Верификация Telegram данных
        telegram_data = {
            "user": {
                "id": 123456789,
                "first_name": "Test",
                "last_name": "User",
                "username": "test_user"
            },
            "auth_date": int(time.time()),
            "hash": "test_hash"
        }
        
        response = await self.make_request("POST", "/api/auth/telegram/verify", telegram_data)
        assert response.get("success") is True, f"Ошибка верификации: {response}"
        assert response.get("data", {}).get("exists") is False, "Пользователь должен быть не найден"
        
        # 2. Регистрация пользователя
        user_data = {
            "telegram_id": "123456789",
            "username": "test_user",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+79001234567",
            "email": "test@example.com",
            "birth_date": "1990-01-01",
            "is_driver": True,
            "car_model": "Toyota Camry",
            "car_color": "Белый",
            "license_plate": "А123БВ77"
        }
        
        response = await self.make_request("POST", "/api/auth/register", user_data)
        assert response.get("success") is True, f"Ошибка регистрации: {response}"
        assert "user" in response.get("data", {}), "Должны быть данные пользователя"
        
        print("✅ Регистрация пользователя прошла успешно")
    
    async def test_user_login_flow(self):
        """Тест входа пользователя"""
        print("🧪 Тестирование входа пользователя...")
        
        # Вход через Telegram
        login_data = {
            "user": {
                "id": 123456789,
                "first_name": "Test",
                "last_name": "User",
                "username": "test_user"
            },
            "auth_date": int(time.time()),
            "hash": "test_hash"
        }
        
        response = await self.make_request("POST", "/api/auth/login", login_data)
        assert response.get("success") is True, f"Ошибка входа: {response}"
        
        # Сохраняем токен для последующих запросов
        data = response.get("data", {})
        self.access_token = data.get("access_token")
        assert self.access_token, "Должен быть получен access token"
        
        print("✅ Вход пользователя прошел успешно")
    
    async def test_ride_creation_flow(self):
        """Тест создания поездки"""
        print("🧪 Тестирование создания поездки...")
        
        # Создание поездки
        ride_data = {
            "from_location": "Москва",
            "to_location": "Санкт-Петербург",
            "departure_time": "2024-01-15T10:00:00",
            "seats_available": 3,
            "price": 1500,
            "description": "Тестовая поездка"
        }
        
        response = await self.make_request("POST", "/api/rides/", ride_data)
        assert response.get("success") is True, f"Ошибка создания поездки: {response}"
        
        ride_id = response.get("data", {}).get("ride", {}).get("id")
        assert ride_id, "Должен быть получен ID поездки"
        
        print("✅ Создание поездки прошло успешно")
        return ride_id
    
    async def test_ride_search_flow(self):
        """Тест поиска поездок"""
        print("🧪 Тестирование поиска поездок...")
        
        # Поиск поездок
        search_params = {
            "from_location": "Москва",
            "to_location": "Санкт-Петербург",
            "date": "2024-01-15"
        }
        
        # Преобразуем параметры в query string
        query_string = "&".join([f"{k}={v}" for k, v in search_params.items()])
        response = await self.make_request("GET", f"/api/rides/search?{query_string}")
        
        assert response.get("success") is True, f"Ошибка поиска поездок: {response}"
        assert "rides" in response.get("data", {}), "Должен быть список поездок"
        
        print("✅ Поиск поездок прошел успешно")
    
    async def test_rating_flow(self):
        """Тест системы рейтингов"""
        print("🧪 Тестирование системы рейтингов...")
        
        # Создание рейтинга
        rating_data = {
            "target_user_id": 1,
            "ride_id": 1,
            "rating": 5,
            "comment": "Отличный водитель, поездка прошла комфортно"
        }
        
        response = await self.make_request("POST", "/api/ratings/", rating_data)
        assert response.get("success") is True, f"Ошибка создания рейтинга: {response}"
        
        # Получение рейтингов пользователя
        response = await self.make_request("GET", "/api/ratings/user/1")
        assert response.get("success") is True, f"Ошибка получения рейтингов: {response}"
        
        print("✅ Система рейтингов работает корректно")
    
    async def test_notification_flow(self):
        """Тест системы уведомлений"""
        print("🧪 Тестирование системы уведомлений...")
        
        # Настройка уведомлений
        notification_settings = {
            "email_notifications": True,
            "push_notifications": True,
            "sms_notifications": False,
            "ride_updates": True,
            "new_messages": True,
            "rating_updates": True
        }
        
        response = await self.make_request("PUT", "/api/notifications/settings/1", notification_settings)
        assert response.get("success") is True, f"Ошибка настройки уведомлений: {response}"
        
        # Получение настроек уведомлений
        response = await self.make_request("GET", "/api/notifications/settings/1")
        assert response.get("success") is True, f"Ошибка получения настроек: {response}"
        
        print("✅ Система уведомлений работает корректно")
    
    async def test_chat_flow(self):
        """Тест системы чата"""
        print("🧪 Тестирование системы чата...")
        
        # Отправка сообщения
        message_data = {
            "receiver_id": 2,
            "content": "Привет! Есть место в поездке?",
            "ride_id": 1
        }
        
        response = await self.make_request("POST", "/api/chat/send", message_data)
        assert response.get("success") is True, f"Ошибка отправки сообщения: {response}"
        
        # Получение истории сообщений
        response = await self.make_request("GET", "/api/chat/history/1")
        assert response.get("success") is True, f"Ошибка получения истории: {response}"
        
        print("✅ Система чата работает корректно")
    
    async def test_file_upload_flow(self):
        """Тест загрузки файлов"""
        print("🧪 Тестирование загрузки файлов...")
        
        # Создание тестового файла
        test_file_content = b"Test file content"
        
        # Симуляция загрузки файла
        upload_data = {
            "file_type": "avatar",
            "file_name": "test_avatar.jpg",
            "file_size": len(test_file_content),
            "file_hash": "test_hash"
        }
        
        response = await self.make_request("POST", "/api/upload/", upload_data)
        assert response.get("success") is True, f"Ошибка загрузки файла: {response}"
        
        print("✅ Загрузка файлов работает корректно")
    
    async def test_error_handling(self):
        """Тест обработки ошибок"""
        print("🧪 Тестирование обработки ошибок...")
        
        # Тест с некорректными данными
        invalid_data = {
            "invalid_field": "invalid_value"
        }
        
        response = await self.make_request("POST", "/api/auth/register", invalid_data)
        assert response.get("success") is False, "Должна быть ошибка валидации"
        assert "error_code" in response, "Должен быть код ошибки"
        
        # Тест с несуществующим endpoint
        response = await self.make_request("GET", "/api/nonexistent")
        assert response.get("success") is False, "Должна быть ошибка 404"
        
        print("✅ Обработка ошибок работает корректно")
    
    async def test_performance_metrics(self):
        """Тест метрик производительности"""
        print("🧪 Тестирование метрик производительности...")
        
        # Отправка метрик
        metrics_data = {
            "api_calls": 10,
            "errors": 2,
            "response_time": 150,
            "cache_hits": 8,
            "cache_misses": 2
        }
        
        response = await self.make_request("POST", "/api/monitoring/metrics", metrics_data)
        assert response.get("success") is True, f"Ошибка отправки метрик: {response}"
        
        # Получение статистики
        response = await self.make_request("GET", "/api/monitoring/stats")
        assert response.get("success") is True, f"Ошибка получения статистики: {response}"
        
        print("✅ Система метрик работает корректно")
    
    async def run_all_tests(self):
        """Запуск всех E2E тестов"""
        print("🚀 Запуск E2E тестов интеграции...")
        
        await self.setup()
        
        try:
            # Основные тесты
            await self.test_user_registration_flow()
            await self.test_user_login_flow()
            await self.test_ride_creation_flow()
            await self.test_ride_search_flow()
            await self.test_rating_flow()
            await self.test_notification_flow()
            await self.test_chat_flow()
            await self.test_file_upload_flow()
            await self.test_error_handling()
            await self.test_performance_metrics()
            
            print("🎉 Все E2E тесты прошли успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка в E2E тестах: {str(e)}")
            raise
        finally:
            await self.teardown()

# Функции для запуска тестов
async def run_e2e_tests():
    """Запуск E2E тестов"""
    tester = E2EIntegrationTest()
    await tester.run_all_tests()

def test_e2e_integration():
    """Синхронная обертка для pytest"""
    asyncio.run(run_e2e_tests())

if __name__ == "__main__":
    # Запуск тестов напрямую
    asyncio.run(run_e2e_tests()) 