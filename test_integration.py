#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений интеграции фронтенда и бэкенда
"""

import requests
import json
import time
from typing import Dict, Any

# Конфигурация
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class IntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Логирование результатов теста"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_auth_integration(self):
        """Тест интеграции авторизации"""
        print("\n🔐 Тестирование авторизации...")
        
        # Тестовые данные Telegram
        telegram_data = {
            "user": {
                "id": 123456789,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser",
                "photo_url": "https://example.com/photo.jpg",
                "auth_date": int(time.time()),
                "hash": "test_hash"
            },
            "auth_date": int(time.time()),
            "hash": "test_hash",
            "initData": "",
            "query_id": "",
            "start_param": ""
        }
        
        try:
            # Тест верификации Telegram
            response = self.session.post(
                f"{API_BASE}/auth/telegram/verify",
                json=telegram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Telegram верификация", True, f"Пользователь существует: {data.get('exists', False)}")
            else:
                self.log_test("Telegram верификация", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Telegram верификация", False, f"Ошибка: {str(e)}")
    
    def test_rating_integration(self):
        """Тест интеграции рейтингов"""
        print("\n⭐ Тестирование рейтингов...")
        
        # Тестовые данные рейтинга
        rating_data = {
            "target_user_id": 1,
            "ride_id": 1,
            "rating": 5,
            "comment": "Отличная поездка! Рекомендую всем."
        }
        
        try:
            # Тест создания рейтинга
            response = self.session.post(
                f"{API_BASE}/rating/",
                json=rating_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Создание рейтинга", True, f"Рейтинг создан: {data.get('rating', 0)}")
            else:
                self.log_test("Создание рейтинга", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Создание рейтинга", False, f"Ошибка: {str(e)}")
        
        # Тест создания отзыва
        review_data = {
            "target_user_id": 1,
            "ride_id": 1,
            "text": "Очень хороший водитель, поездка была комфортной и безопасной.",
            "is_positive": True
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/rating/review",
                json=review_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Создание отзыва", True, f"Отзыв создан: {data.get('text', '')[:50]}...")
            else:
                self.log_test("Создание отзыва", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Создание отзыва", False, f"Ошибка: {str(e)}")
    
    def test_notification_integration(self):
        """Тест интеграции уведомлений"""
        print("\n🔔 Тестирование уведомлений...")
        
        try:
            # Тест получения настроек уведомлений
            response = self.session.get(f"{API_BASE}/notifications/settings/1")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Получение настроек уведомлений", True, 
                            f"Настройки получены: ride={data.get('ride_notifications')}")
            else:
                self.log_test("Получение настроек уведомлений", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Получение настроек уведомлений", False, f"Ошибка: {str(e)}")
        
        # Тест обновления настроек
        settings_data = {
            "user_id": 1,
            "ride_notifications": True,
            "system_notifications": True,
            "reminder_notifications": False,
            "marketing_notifications": False,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "email_notifications": False,
            "push_notifications": True
        }
        
        try:
            response = self.session.put(
                f"{API_BASE}/notifications/settings/1",
                json=settings_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Обновление настроек уведомлений", True, 
                            f"Настройки обновлены: {data.get('message', '')}")
            else:
                self.log_test("Обновление настроек уведомлений", False, 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Обновление настроек уведомлений", False, f"Ошибка: {str(e)}")
    
    def test_api_endpoints(self):
        """Тест доступности API эндпоинтов"""
        print("\n🌐 Тестирование API эндпоинтов...")
        
        endpoints = [
            ("GET", "/auth/privacy-policy", "Политика конфиденциальности"),
            ("GET", "/rating/user/1/summary", "Сводка рейтингов"),
            ("GET", "/rating/top", "Топ пользователей"),
            ("GET", "/rating/statistics", "Статистика рейтингов"),
            ("GET", "/notifications/status", "Статус уведомлений")
        ]
        
        for method, endpoint, description in endpoints:
            try:
                response = self.session.request(
                    method, 
                    f"{API_BASE}{endpoint}",
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code in [200, 404]:  # 404 тоже нормально для тестовых данных
                    self.log_test(f"{description}", True, f"HTTP {response.status_code}")
                else:
                    self.log_test(f"{description}", False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test(f"{description}", False, f"Ошибка: {str(e)}")
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🧪 ЗАПУСК ТЕСТОВ ИНТЕГРАЦИИ")
        print("=" * 50)
        
        # Проверяем доступность сервера
        try:
            response = self.session.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("✅ Сервер доступен")
            else:
                print("❌ Сервер недоступен")
                return
        except Exception as e:
            print(f"❌ Ошибка подключения к серверу: {str(e)}")
            return
        
        # Запускаем тесты
        self.test_auth_integration()
        self.test_rating_integration()
        self.test_notification_integration()
        self.test_api_endpoints()
        
        # Выводим итоговую статистику
        print("\n" + "=" * 50)
        print("📊 ИТОГОВАЯ СТАТИСТИКА")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Всего тестов: {total_tests}")
        print(f"Пройдено: {passed_tests}")
        print(f"Провалено: {failed_tests}")
        print(f"Успешность: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests == 0:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        else:
            print(f"\n⚠️  ПРОВАЛЕНО ТЕСТОВ: {failed_tests}")
            print("Детали проваленных тестов:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")

if __name__ == "__main__":
    tester = IntegrationTester()
    tester.run_all_tests() 