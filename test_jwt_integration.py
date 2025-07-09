#!/usr/bin/env python3
"""
Тестирование JWT авторизации и новых функций Фазы 2
"""

import requests
import json
import time
import sys
import os

# Конфигурация
BASE_URL = "https://pax-backend-2gng.onrender.com"
API_BASE = f"{BASE_URL}/api"

# Тестовые данные
TEST_TELEGRAM_DATA = {
    "user": {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "language_code": "ru",
        "photo_url": "https://t.me/i/userpic/320/testuser.jpg"
    },
    "auth_date": int(time.time()),
    "hash": "test_hash_for_development",
    "initData": "",
    "query_id": "",
    "start_param": ""
}

def print_section(title):
    """Вывод заголовка секции"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_result(test_name, success, details=None):
    """Вывод результата теста"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   {details}")

def test_health_check():
    """Тест health check"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            details += f", Database: {data.get('database', 'unknown')}"
        return success, details
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_api_info():
    """Тест API info"""
    try:
        response = requests.get(f"{BASE_URL}/api/info", timeout=10)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            details += f", Version: {data.get('version', 'unknown')}"
        return success, details
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_telegram_verification():
    """Тест верификации Telegram"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/telegram/verify",
            json=TEST_TELEGRAM_DATA,
            timeout=10
        )
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            details += f", Exists: {data.get('exists', 'unknown')}"
        return success, details
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_jwt_login():
    """Тест JWT логина"""
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=TEST_TELEGRAM_DATA,
            timeout=10
        )
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            has_tokens = 'tokens' in data and 'access_token' in data['tokens']
            details += f", Has tokens: {has_tokens}"
            return success, details, data.get('tokens', {})
        return success, details, None
    except Exception as e:
        return False, f"Error: {str(e)}", None

def test_jwt_refresh(tokens):
    """Тест обновления JWT токенов"""
    if not tokens or 'refresh_token' not in tokens:
        return False, "No refresh token available"
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/refresh",
            json={"refresh_token": tokens['refresh_token']},
            timeout=10
        )
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            has_new_tokens = 'tokens' in data and 'access_token' in data['tokens']
            details += f", Has new tokens: {has_new_tokens}"
        return success, details
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_protected_endpoint(access_token):
    """Тест защищенного эндпоинта"""
    if not access_token:
        return False, "No access token available"
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers=headers,
            timeout=10
        )
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            details += f", User ID: {data.get('user', {}).get('id', 'unknown')}"
        return success, details
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_rate_limiting():
    """Тест rate limiting"""
    try:
        # Делаем несколько запросов подряд
        responses = []
        for i in range(5):
            response = requests.get(f"{API_BASE}/auth/telegram/verify", timeout=5)
            responses.append(response.status_code)
            time.sleep(0.1)  # Небольшая задержка
        
        # Проверяем, что все запросы прошли (не получили 429)
        success = all(status != 429 for status in responses)
        details = f"Response codes: {responses}"
        return success, details
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_file_upload_with_auth(access_token):
    """Тест загрузки файла с авторизацией"""
    if not access_token:
        return False, "No access token available"
    
    try:
        # Создаем тестовый файл
        test_file_content = b"test file content"
        files = {"file": ("test.txt", test_file_content, "text/plain")}
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.post(
            f"{API_BASE}/upload/avatar",
            files=files,
            headers=headers,
            timeout=10
        )
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            details += f", File URL: {data.get('file_url', 'unknown')}"
        return success, details
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ JWT АВТОРИЗАЦИИ И НОВЫХ ФУНКЦИЙ")
    print(f"Target: {BASE_URL}")
    
    # Счетчики результатов
    total_tests = 0
    passed_tests = 0
    tokens = None
    
    # Тест 1: Health Check
    print_section("1. HEALTH CHECK")
    total_tests += 1
    success, details = test_health_check()
    print_result("Health Check", success, details)
    if success:
        passed_tests += 1
    
    # Тест 2: API Info
    print_section("2. API INFO")
    total_tests += 1
    success, details = test_api_info()
    print_result("API Info", success, details)
    if success:
        passed_tests += 1
    
    # Тест 3: Telegram Verification
    print_section("3. TELEGRAM VERIFICATION")
    total_tests += 1
    success, details = test_telegram_verification()
    print_result("Telegram Verification", success, details)
    if success:
        passed_tests += 1
    
    # Тест 4: JWT Login
    print_section("4. JWT LOGIN")
    total_tests += 1
    success, details, tokens = test_jwt_login()
    print_result("JWT Login", success, details)
    if success:
        passed_tests += 1
    
    # Тест 5: JWT Refresh (если есть токены)
    if tokens:
        print_section("5. JWT REFRESH")
        total_tests += 1
        success, details = test_jwt_refresh(tokens)
        print_result("JWT Refresh", success, details)
        if success:
            passed_tests += 1
    
    # Тест 6: Protected Endpoint
    if tokens and 'access_token' in tokens:
        print_section("6. PROTECTED ENDPOINT")
        total_tests += 1
        success, details = test_protected_endpoint(tokens['access_token'])
        print_result("Protected Endpoint", success, details)
        if success:
            passed_tests += 1
    
    # Тест 7: Rate Limiting
    print_section("7. RATE LIMITING")
    total_tests += 1
    success, details = test_rate_limiting()
    print_result("Rate Limiting", success, details)
    if success:
        passed_tests += 1
    
    # Тест 8: File Upload with Auth
    if tokens and 'access_token' in tokens:
        print_section("8. FILE UPLOAD WITH AUTH")
        total_tests += 1
        success, details = test_file_upload_with_auth(tokens['access_token'])
        print_result("File Upload with Auth", success, details)
        if success:
            passed_tests += 1
    
    # Итоговые результаты
    print_section("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
    print(f"Всего тестов: {total_tests}")
    print(f"Пройдено: {passed_tests}")
    print(f"Провалено: {total_tests - passed_tests}")
    print(f"Успешность: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} ТЕСТОВ ПРОВАЛЕНО")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 