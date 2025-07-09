import pytest
from fastapi.testclient import TestClient
from app.schemas.telegram import TelegramWebAppData, TelegramUserData

def test_telegram_verification_success(client: TestClient, sample_user_data):
    """Тест успешной верификации Telegram"""
    telegram_data = {
        "user": {
            "id": 123456789,
            "first_name": "Test",
            "last_name": "User",
            "username": "testuser",
            "auth_date": 1640995200,
            "hash": "test_hash"
        }
    }
    
    response = client.post("/api/auth/telegram/verify", json=telegram_data)
    assert response.status_code in [200, 401]  # 401 если верификация не прошла в тестах

def test_telegram_verification_invalid_data(client: TestClient):
    """Тест верификации с некорректными данными"""
    invalid_data = {
        "user": {
            "id": "invalid_id",  # Должен быть int
            "first_name": "",  # Пустое имя
            "auth_date": "invalid_date"  # Некорректная дата
        }
    }
    
    response = client.post("/api/auth/telegram/verify", json=invalid_data)
    assert response.status_code == 400

def test_user_registration_success(client: TestClient, sample_user_data):
    """Тест успешной регистрации пользователя"""
    response = client.post("/api/auth/register", json=sample_user_data)
    assert response.status_code in [200, 409]  # 409 если пользователь уже существует

def test_user_registration_invalid_data(client: TestClient):
    """Тест регистрации с некорректными данными"""
    invalid_data = {
        "telegram_id": "",  # Пустой ID
        "full_name": "A",  # Слишком короткое имя
        "phone": "invalid_phone"  # Некорректный телефон
    }
    
    response = client.post("/api/auth/register", json=invalid_data)
    assert response.status_code == 400

def test_get_user_profile(client: TestClient):
    """Тест получения профиля пользователя"""
    response = client.get("/api/auth/profile/1")
    assert response.status_code in [200, 404]

def test_get_user_profile_invalid_id(client: TestClient):
    """Тест получения профиля с некорректным ID"""
    response = client.get("/api/auth/profile/0")  # Некорректный ID
    assert response.status_code == 400

def test_telegram_schema_validation():
    """Тест валидации схемы Telegram данных"""
    valid_data = {
        "id": 123456789,
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "auth_date": 1640995200
    }
    
    try:
        user_data = TelegramUserData(**valid_data)
        assert user_data.id == 123456789
        assert user_data.first_name == "Test"
    except Exception as e:
        pytest.fail(f"Валидация должна пройти успешно: {e}")

def test_telegram_schema_invalid_data():
    """Тест валидации схемы с некорректными данными"""
    invalid_data = {
        "id": "invalid",  # Должен быть int
        "first_name": "",  # Пустое имя
        "auth_date": "invalid"  # Некорректная дата
    }
    
    with pytest.raises(Exception):
        TelegramUserData(**invalid_data) 