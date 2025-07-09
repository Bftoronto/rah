# Архитектура Backend

## Обзор

Backend приложения Pax построен с использованием современной многослойной архитектуры, обеспечивающей высокую производительность, безопасность и масштабируемость.

## Структура проекта

```
backend/
├── app/                          # Основное приложение
│   ├── api/                      # API endpoints (Controller layer)
│   │   ├── auth.py              # Аутентификация
│   │   ├── rides.py             # Поездки
│   │   ├── chat.py              # Чат
│   │   ├── moderation.py        # Модерация
│   │   ├── notifications.py     # Уведомления
│   │   ├── rating.py            # Рейтинги
│   │   ├── upload.py            # Загрузка файлов
│   │   └── profile.py           # Профили пользователей
│   ├── config/                   # Конфигурация
│   │   ├── settings.py          # Основные настройки
│   │   ├── database.py          # Настройки БД
│   │   ├── security.py          # Настройки безопасности
│   │   └── logging.py           # Настройки логирования
│   ├── services/                 # Бизнес-логика (Service layer)
│   │   ├── auth_service.py      # Сервис аутентификации
│   │   ├── ride_service.py      # Сервис поездок
│   │   ├── chat_service.py      # Сервис чата
│   │   ├── moderation_service.py # Сервис модерации
│   │   ├── notification_service.py # Сервис уведомлений
│   │   ├── rating_service.py    # Сервис рейтингов
│   │   ├── upload_service.py    # Сервис загрузки
│   │   └── profile_service.py   # Сервис профилей
│   ├── models/                   # Модели данных (Data layer)
│   │   ├── user.py              # Модель пользователя
│   │   ├── ride.py              # Модель поездки
│   │   ├── chat.py              # Модель чата
│   │   ├── moderation.py        # Модель модерации
│   │   ├── notification.py      # Модель уведомления
│   │   ├── rating.py            # Модель рейтинга
│   │   └── upload.py            # Модель загрузки
│   ├── schemas/                  # Pydantic схемы (DTO layer)
│   │   ├── user.py              # Схемы пользователя
│   │   ├── ride.py              # Схемы поездки
│   │   ├── chat.py              # Схемы чата
│   │   ├── moderation.py        # Схемы модерации
│   │   ├── notification.py      # Схемы уведомления
│   │   ├── rating.py            # Схемы рейтинга
│   │   ├── upload.py            # Схемы загрузки
│   │   └── telegram.py          # Схемы Telegram данных
│   ├── repositories/             # Репозитории (Repository layer)
│   │   └── user_repository.py   # Репозиторий пользователей
│   ├── interfaces/               # Интерфейсы (Interface layer)
│   │   ├── auth.py              # Интерфейс аутентификации
│   │   └── user_repository.py   # Интерфейс репозитория
│   ├── validators/               # Валидаторы
│   │   └── data_validator.py    # Валидатор данных
│   ├── middleware/               # Middleware
│   │   └── performance.py       # Мониторинг производительности
│   ├── monitoring/               # Мониторинг
│   │   └── metrics.py           # Система метрик
│   ├── utils/                    # Утилиты
│   │   ├── logger.py            # Система логирования
│   │   ├── security.py          # Безопасность
│   │   ├── telegram.py          # Telegram интеграция
│   │   └── validators.py        # Валидаторы
│   ├── database.py               # Конфигурация БД
│   └── main.py                   # Точка входа
├── tests/                        # Тесты
│   ├── conftest.py              # Конфигурация pytest
│   ├── test_auth.py             # Тесты аутентификации
│   └── ...                      # Другие тесты
├── scripts/                      # Скрипты развертывания
│   └── deploy.py                # Скрипт развертывания
├── docs/                         # Документация
│   └── API.md                   # Документация API
├── monitoring/                   # Мониторинг
│   └── metrics.py               # Система метрик
├── migrations/                   # Миграции БД
├── requirements_enhanced.txt     # Зависимости
└── README.md                     # Документация проекта
```

## Архитектурные принципы

### 1. Многослойная архитектура (Layered Architecture)

```
┌─────────────────────────────────────┐
│           API Layer                 │  ← FastAPI endpoints
├─────────────────────────────────────┤
│         Service Layer               │  ← Бизнес-логика
├─────────────────────────────────────┤
│       Repository Layer              │  ← Доступ к данным
├─────────────────────────────────────┤
│         Data Layer                  │  ← SQLAlchemy models
└─────────────────────────────────────┘
```

### 2. Dependency Injection

Все зависимости инжектируются через FastAPI dependency injection:

```python
def get_auth_service() -> AuthService:
    return AuthService()

@router.post("/login")
async def login(
    credentials: LoginCredentials,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.authenticate(credentials)
```

### 3. Interface Segregation

Интерфейсы разделены по функциональности:

```python
class IAuthService(ABC):
    @abstractmethod
    async def authenticate(self, credentials: LoginCredentials) -> AuthResult:
        pass

class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass
```

### 4. Single Responsibility Principle

Каждый класс имеет одну ответственность:

- **API Controllers** - обработка HTTP запросов
- **Services** - бизнес-логика
- **Repositories** - доступ к данным
- **Models** - структура данных
- **Schemas** - валидация данных

## Безопасность

### 1. Валидация входных данных

```python
class TelegramUserData(BaseModel):
    id: int = Field(..., gt=0)
    first_name: str = Field(..., min_length=1, max_length=64)
    auth_date: int = Field(..., gt=0)
```

### 2. Аутентификация

- JWT токены для API
- Telegram WebApp аутентификация
- Rate limiting для защиты от атак

### 3. Авторизация

- Роли пользователей (driver, passenger, admin)
- Проверка прав доступа к ресурсам

## Производительность

### 1. Оптимизация запросов

```python
# Использование joinedload для оптимизации
rides = db.query(Ride).options(
    joinedload(Ride.driver),
    joinedload(Ride.passengers)
).filter(Ride.status == "active").all()
```

### 2. Кэширование

- Redis для кэширования частых запросов
- In-memory кэш для метрик

### 3. Мониторинг

- Метрики производительности
- Логирование запросов
- Health checks

## Масштабируемость

### 1. Горизонтальное масштабирование

- Stateless API endpoints
- Внешняя база данных
- Load balancer ready

### 2. Версионирование API

```python
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(auth.router, prefix="/api/v2/auth")
```

### 3. Микросервисная готовность

- Модульная архитектура
- Независимые сервисы
- Event-driven коммуникация

## Тестирование

### 1. Unit тесты

```python
def test_auth_service_authenticate():
    service = AuthService()
    result = service.authenticate(valid_credentials)
    assert result.success == True
```

### 2. Integration тесты

```python
def test_telegram_verification_integration(client):
    response = client.post("/api/auth/telegram/verify", json=telegram_data)
    assert response.status_code == 200
```

### 3. Performance тесты

- Нагрузочное тестирование
- Тестирование производительности БД
- Мониторинг метрик

## Развертывание

### 1. Docker

```dockerfile
FROM python:3.11-slim
COPY requirements_enhanced.txt .
RUN pip install -r requirements_enhanced.txt
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. CI/CD

- Автоматические тесты
- Автоматическое развертывание
- Мониторинг здоровья

### 3. Environment Management

```python
class Settings(BaseSettings):
    environment: str = Field(default="production")
    debug: bool = Field(default=False)
    database_url: str = Field(env="DATABASE_URL")
```

## Мониторинг и логирование

### 1. Структурированное логирование

```python
logger.info("User authenticated", {
    "user_id": user.id,
    "method": "telegram",
    "duration_ms": duration
})
```

### 2. Метрики

- API запросы/сек
- Время ответа
- Ошибки
- Использование ресурсов

### 3. Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": time.time()
    }
```

## Заключение

Архитектура обеспечивает:

- ✅ **Высокую производительность** через оптимизацию и кэширование
- ✅ **Безопасность** через валидацию и аутентификацию
- ✅ **Масштабируемость** через модульную архитектуру
- ✅ **Надежность** через тестирование и мониторинг
- ✅ **Поддерживаемость** через четкое разделение ответственности 