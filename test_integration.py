#!/usr/bin/env python3
"""
Комплексные тесты интеграции фронтенда и бэкенда
Проверяет совместимость API, схем данных и обработки ошибок
"""

import asyncio
import json
import requests
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

# Конфигурация тестов
BASE_URL = "https://pax-backend-2gng.onrender.com"
TEST_USER_DATA = {
    "id": 123456789,
    "first_name": "Test",
    "last_name": "User",
    "username": "testuser",
    "photo_url": "https://t.me/i/userpic/320/test.jpg",
    "auth_date": int(datetime.now().timestamp()),
    "hash": "test_hash_123"
}

class IntegrationTestSuite:
    """Комплексные тесты интеграции"""
    
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.test_user_id = None
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Логирование результатов тестов"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"[{timestamp}] {status_icon} {test_name}: {details}")
    
    def test_health_check(self) -> bool:
        """Тест доступности API"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", "PASS", f"API доступен, версия: {data.get('version', 'unknown')}")
                return True
            else:
                self.log_test("Health Check", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", "FAIL", f"Ошибка подключения: {str(e)}")
            return False
    
    def test_telegram_auth_schema(self) -> bool:
        """Тест схемы авторизации Telegram"""
        try:
            auth_data = {
                "user": TEST_USER_DATA,
                "auth_date": TEST_USER_DATA["auth_date"],
                "hash": TEST_USER_DATA["hash"]
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/auth/telegram/verify",
                json=auth_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 400]:  # 400 - ожидаемо для тестовых данных
                self.log_test("Telegram Auth Schema", "PASS", "Схема валидна")
                return True
            else:
                self.log_test("Telegram Auth Schema", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Telegram Auth Schema", "FAIL", f"Ошибка: {str(e)}")
            return False
    
    def test_rides_search_api(self) -> bool:
        """Тест API поиска поездок"""
        try:
            params = {
                "from_location": "Москва",
                "to_location": "Санкт-Петербург",
                "date_from": datetime.now().isoformat(),
                "limit": 10
            }
            
            response = self.session.get(
                f"{BASE_URL}/api/rides/search",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Rides Search API", "PASS", f"Найдено {len(data)} поездок")
                    return True
                else:
                    self.log_test("Rides Search API", "FAIL", "Неверный формат ответа")
                    return False
            else:
                self.log_test("Rides Search API", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Rides Search API", "FAIL", f"Ошибка: {str(e)}")
            return False
    
    def test_file_upload_schema(self) -> bool:
        """Тест схемы загрузки файлов"""
        try:
            # Создаем тестовый файл
            test_file_content = b"test image content"
            
            files = {"file": ("test.jpg", test_file_content, "image/jpeg")}
            data = {"file_type": "avatar"}
            
            response = self.session.post(
                f"{BASE_URL}/api/upload/",
                files=files,
                data=data
            )
            
            # Ожидаем 401 (нет авторизации) или 400 (неверные данные)
            if response.status_code in [401, 400]:
                self.log_test("File Upload Schema", "PASS", "Схема валидна")
                return True
            else:
                self.log_test("File Upload Schema", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("File Upload Schema", "FAIL", f"Ошибка: {str(e)}")
            return False
    
    def test_chat_api_schema(self) -> bool:
        """Тест схемы чата"""
        try:
            # Тест получения чатов (без авторизации)
            response = self.session.get(f"{BASE_URL}/api/chat/")
            
            if response.status_code == 401:  # Ожидаем 401 без авторизации
                self.log_test("Chat API Schema", "PASS", "Схема валидна")
                return True
            else:
                self.log_test("Chat API Schema", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Chat API Schema", "FAIL", f"Ошибка: {str(e)}")
            return False
    
    def test_rating_api_schema(self) -> bool:
        """Тест схемы рейтингов"""
        try:
            # Тест получения рейтингов
            response = self.session.get(f"{BASE_URL}/api/rating/statistics")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    self.log_test("Rating API Schema", "PASS", "Схема валидна")
                    return True
                else:
                    self.log_test("Rating API Schema", "FAIL", "Неверный формат ответа")
                    return False
            else:
                self.log_test("Rating API Schema", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Rating API Schema", "FAIL", f"Ошибка: {str(e)}")
            return False
    
    def test_notifications_api_schema(self) -> bool:
        """Тест схемы уведомлений"""
        try:
            # Тест статуса уведомлений
            response = self.session.get(f"{BASE_URL}/api/notifications/status")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    self.log_test("Notifications API Schema", "PASS", "Схема валидна")
                    return True
                else:
                    self.log_test("Notifications API Schema", "FAIL", "Неверный формат ответа")
                    return False
            else:
                self.log_test("Notifications API Schema", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Notifications API Schema", "FAIL", f"Ошибка: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Тест обработки ошибок"""
        try:
            # Тест несуществующего эндпоинта
            response = self.session.get(f"{BASE_URL}/api/nonexistent")
            
            if response.status_code == 404:
                self.log_test("Error Handling", "PASS", "404 обрабатывается корректно")
                return True
            else:
                self.log_test("Error Handling", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", "FAIL", f"Ошибка: {str(e)}")
            return False
    
    def test_cors_headers(self) -> bool:
        """Тест CORS заголовков"""
        try:
            response = self.session.options(f"{BASE_URL}/api/auth/")
            
            if response.status_code == 200:
                cors_headers = response.headers.get("Access-Control-Allow-Origin")
                if cors_headers:
                    self.log_test("CORS Headers", "PASS", "CORS настроен")
                    return True
                else:
                    self.log_test("CORS Headers", "FAIL", "CORS заголовки отсутствуют")
                    return False
            else:
                self.log_test("CORS Headers", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("CORS Headers", "FAIL", f"Ошибка: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🔍 ЗАПУСК КОМПЛЕКСНЫХ ТЕСТОВ ИНТЕГРАЦИИ")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Telegram Auth Schema", self.test_telegram_auth_schema),
            ("Rides Search API", self.test_rides_search_api),
            ("File Upload Schema", self.test_file_upload_schema),
            ("Chat API Schema", self.test_chat_api_schema),
            ("Rating API Schema", self.test_rating_api_schema),
            ("Notifications API Schema", self.test_notifications_api_schema),
            ("Error Handling", self.test_error_handling),
            ("CORS Headers", self.test_cors_headers)
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                self.log_test(test_name, "FAIL", f"Исключение: {str(e)}")
                results[test_name] = False
        
        # Вывод результатов
        print("\n" + "=" * 60)
        print(f"📊 РЕЗУЛЬТАТЫ ТЕСТОВ: {passed}/{total} пройдено")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"🎯 Процент успешности: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ Интеграция в хорошем состоянии")
        elif success_rate >= 60:
            print("⚠️  Интеграция требует внимания")
        else:
            print("❌ Критические проблемы интеграции")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": success_rate,
            "results": results
        }

def main():
    """Главная функция"""
    test_suite = IntegrationTestSuite()
    results = test_suite.run_all_tests()
    
    # Сохранение результатов
    with open("integration_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Результаты сохранены в integration_test_results.json")
    
    return results["success_rate"] >= 60

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 