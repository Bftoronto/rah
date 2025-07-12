# Backend (FastAPI)

Бэкенд для ride-sharing/marketplace приложения (FastAPI, PostgreSQL, Redis, Docker, Alembic, Pytest).

## Структура

- `app/` — основное приложение (FastAPI, бизнес-логика, модели, схемы, роуты)
- `migrations/` — Alembic миграции
- `tests/` — тесты (pytest)
- `requirements.txt` — зависимости
- `Dockerfile` — контейнеризация
- `alembic.ini` — конфиг миграций
- `.env` — переменные окружения

## Запуск

1. `docker-compose up --build` — запуск всего стека
2. Документация API: http://localhost:8000/docs

## Миграции
- `alembic revision --autogenerate -m "init"`
- `alembic upgrade head`

## Тесты
- `pytest`

## Интеграция с фронтом
- Все методы API соответствуют ожиданиям фронта (см. assets/js/api.js)
- CORS и HTTPS поддерживаются
- Поддержка Telegram Login и Mini App

## Мониторинг и метрики

Для работы эндпоинта `/api/metrics` требуется пакет `psutil`.
Установите зависимости из requirements.txt:

```
pip install -r requirements.txt
```

---

**Вся структура и код соответствуют фронтенду и требованиям Telegram Mini App.** 