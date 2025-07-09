#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции фронтенда и бэкенда
Проверяет все основные API эндпоинты и их совместимость
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, List

# Конфигурация
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class IntegrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        self.current_user = None
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Логирование результата теста"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": timestamp
        }
        self.results.append(result)
        print(f"[{timestamp}] {status} {test_name}")
        if details:
            print(f"    {details}")
    
    def test_health_check(self) -> bool:
        """Тест health check эндпоинта"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, str(e))
            return False
    
    def test_api_info(self) -> bool:
        """Тест API info эндпоинта"""
        try:
            response = self.session.get(f"{BASE_URL}/api/info")
            if response.status_code == 200:
                data = response.json()
                endpoints = data.get('endpoints', {})
                self.log_test("API Info", True, f"Version: {data.get('version')}, Endpoints: {len(endpoints)}")
                return True
            else:
                self.log_test("API Info", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Info", False, str(e))
            return False
    
    def test_telegram_verification(self) -> bool:
        """Тест верификации Telegram"""
        try:
            # Тестовые данные Telegram
            telegram_data = {
                "user": {
                    "id": 123456789,
                    "first_name": "Test",
                    "last_name": "User",
                    "username": "testuser",
                    "photo_url": "https://t.me/i/userpic/320/testuser.jpg",
                    "auth_date": int(time.time()),
                    "hash": "test_hash"
                },
                "auth_date": int(time.time()),
                "hash": "test_hash",
                "initData": "test_init_data"
            }
            
            response = self.session.post(
                f"{API_BASE}/auth/telegram/verify",
                json=telegram_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [200, 400, 401]:  # Различные возможные ответы
                data = response.json()
                exists = data.get('exists', False)
                self.log_test("Telegram Verification", True, f"User exists: {exists}")
                return True
            else:
                self.log_test("Telegram Verification", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Telegram Verification", False, str(e))
            return False
    
    def test_profile_endpoints(self) -> bool:
        """Тест эндпоинтов профиля"""
        try:
            # Тест получения профиля (может требовать авторизации)
            response = self.session.get(f"{API_BASE}/profile")
            
            if response.status_code in [200, 401]:  # 401 - требует авторизации
                self.log_test("Profile GET", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Profile GET", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Profile GET", False, str(e))
            return False
    
    def test_upload_endpoints(self) -> bool:
        """Тест эндпоинтов загрузки файлов"""
        try:
            # Создаем тестовый файл
            test_file_content = b"test image content"
            
            # Тест загрузки аватара
            files = {'file': ('test_avatar.jpg', test_file_content, 'image/jpeg')}
            response = self.session.post(f"{API_BASE}/upload/avatar", files=files)
            
            if response.status_code in [200, 401]:  # 401 - требует авторизации
                self.log_test("Upload Avatar", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Upload Avatar", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Upload Avatar", False, str(e))
            return False
    
    def test_rides_endpoints(self) -> bool:
        """Тест эндпоинтов поездок"""
        try:
            # Тест поиска поездок
            params = {
                "from_location": "Москва",
                "to_location": "Санкт-Петербург",
                "date_from": "2024-01-15"
            }
            response = self.session.get(f"{API_BASE}/rides/search", params=params)
            
            if response.status_code in [200, 401]:  # 401 - требует авторизации
                self.log_test("Rides Search", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Rides Search", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Rides Search", False, str(e))
            return False
    
    def test_chat_endpoints(self) -> bool:
        """Тест эндпоинтов чата"""
        try:
            # Тест получения сообщений чата
            response = self.session.get(f"{API_BASE}/chat/1/messages")
            
            if response.status_code in [200, 401, 404]:  # 404 - чат не найден
                self.log_test("Chat Messages", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Chat Messages", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Chat Messages", False, str(e))
            return False
    
    def test_rating_endpoints(self) -> bool:
        """Тест эндпоинтов рейтинга"""
        try:
            # Тест получения рейтингов пользователя
            response = self.session.get(f"{API_BASE}/rating/user/1")
            
            if response.status_code in [200, 401, 404]:  # 404 - пользователь не найден
                self.log_test("User Ratings", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("User Ratings", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Ratings", False, str(e))
            return False
    
    def test_notifications_endpoints(self) -> bool:
        """Тест эндпоинтов уведомлений"""
        try:
            # Тест получения уведомлений
            response = self.session.get(f"{API_BASE}/notifications")
            
            if response.status_code in [200, 401]:
                self.log_test("Notifications", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Notifications", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Notifications", False, str(e))
            return False
    
    def test_moderation_endpoints(self) -> bool:
        """Тест эндпоинтов модерации"""
        try:
            # Тест получения отчетов
            response = self.session.get(f"{API_BASE}/moderation/reports")
            
            if response.status_code in [200, 401]:
                self.log_test("Moderation Reports", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Moderation Reports", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Moderation Reports", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Запуск всех тестов"""
        print("🚀 Запуск тестов интеграции фронтенда и бэкенда")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("API Info", self.test_api_info),
            ("Telegram Verification", self.test_telegram_verification),
            ("Profile Endpoints", self.test_profile_endpoints),
            ("Upload Endpoints", self.test_upload_endpoints),
            ("Rides Endpoints", self.test_rides_endpoints),
            ("Chat Endpoints", self.test_chat_endpoints),
            ("Rating Endpoints", self.test_rating_endpoints),
            ("Notifications Endpoints", self.test_notifications_endpoints),
            ("Moderation Endpoints", self.test_moderation_endpoints),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Exception: {str(e)}")
        
        # Вывод итогового отчета
        print("\n" + "=" * 60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"✅ Пройдено: {passed}/{total} ({success_rate:.1f}%)")
        
        # Детальный отчет
        print("\n📋 Детальный отчет:")
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']} - {result['details']}")
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "success_rate": success_rate,
            "results": self.results
        }

def main():
    """Главная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Тестовый скрипт для проверки интеграции фронтенда и бэкенда

Использование:
    python test_integration.py

Опции:
    --help    Показать эту справку

Тесты проверяют:
    - Health check эндпоинт
    - API info эндпоинт
    - Верификацию Telegram
    - Эндпоинты профиля
    - Эндпоинты загрузки файлов
    - Эндпоинты поездок
    - Эндпоинты чата
    - Эндпоинты рейтинга
    - Эндпоинты уведомлений
    - Эндпоинты модерации
        """)
        return
    
    tester = IntegrationTester()
    results = tester.run_all_tests()
    
    # Сохранение результатов в файл
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"integration_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Результаты сохранены в файл: {filename}")
    
    # Возвращаем код выхода
    if results['success_rate'] >= 80:
        print("🎉 Интеграция работает хорошо!")
        sys.exit(0)
    elif results['success_rate'] >= 60:
        print("⚠️  Интеграция работает частично, требуются доработки")
        sys.exit(1)
    else:
        print("❌ Критические проблемы с интеграцией!")
        sys.exit(2)

if __name__ == "__main__":
    main() 