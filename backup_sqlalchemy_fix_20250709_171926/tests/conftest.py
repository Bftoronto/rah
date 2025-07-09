import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.config.settings import get_settings

# Тестовая база данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def db_engine():
    """Создание тестовой базы данных"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    """Создание сессии базы данных для тестов"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session) -> Generator:
    """Создание тестового клиента"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def test_settings():
    """Тестовые настройки"""
    return get_settings()

@pytest.fixture
def sample_user_data():
    """Пример данных пользователя для тестов"""
    return {
        "telegram_id": "123456789",
        "username": "testuser",
        "full_name": "Test User",
        "phone": "+79001234567",
        "city": "Moscow",
        "is_driver": False
    }

@pytest.fixture
def sample_ride_data():
    """Пример данных поездки для тестов"""
    return {
        "from_location": "Moscow",
        "to_location": "St. Petersburg",
        "date": "2024-01-15T10:00:00",
        "price": 1000.0,
        "seats": 3
    } 