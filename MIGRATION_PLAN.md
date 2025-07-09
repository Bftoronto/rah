# ПЛАН МИГРАЦИИ BACKEND: Render → Selectel

## 1. ПРЕДВАРИТЕЛЬНЫЙ АНАЛИЗ

### Текущая архитектура на Render:
- **Backend**: FastAPI + Uvicorn
- **База данных**: PostgreSQL (внешняя)
- **Кэширование**: Redis
- **Прокси**: Nginx
- **Контейнеризация**: Docker Compose
- **SSL**: Let's Encrypt

### Ключевые компоненты:
- FastAPI приложение с 8 API модулями
- PostgreSQL с 8 миграциями
- Redis для кэширования
- Nginx для проксирования
- Telegram Bot интеграция
- Система загрузки файлов

## 2. ПОДГОТОВКА НА SELECTEL

### Системные требования:
- Ubuntu 20.04/22.04 LTS
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7
- Nginx
- Python 3.11+

### Порты для открытия:
- 80 (HTTP)
- 443 (HTTPS)
- 8000 (FastAPI)
- 5432 (PostgreSQL)
- 6379 (Redis)

## 3. МИГРАЦИЯ ДАННЫХ

### Этапы:
1. **Резервное копирование с Render**
2. **Перенос PostgreSQL**
3. **Перенос Redis данных**
4. **Перенос файлов uploads/**
5. **Валидация целостности**

## 4. ПЕРЕНОС КОДА И КОНФИГУРАЦИЙ

### Файлы для переноса:
- `backend/app/` - исходный код
- `backend/migrations/` - миграции БД
- `backend/requirements.txt` - зависимости
- `backend/docker-compose.yml` - контейнеры
- `backend/nginx.conf` - конфигурация Nginx
- `backend/ssl/` - SSL сертификаты

### Environment переменные:
- `DATABASE_URL`
- `TELEGRAM_BOT_TOKEN`
- `SECRET_KEY`
- `REDIS_URL`
- `DEBUG`

## 5. НАСТРОЙКА БЕЗОПАСНОСТИ

### Меры безопасности:
- Firewall (ufw)
- SSL сертификаты
- Rate limiting
- CORS настройки
- Валидация входных данных

## 6. ФИНАЛЬНАЯ ВАЛИДАЦИЯ

### Тестирование:
- Health check endpoints
- API функциональность
- Производительность
- Нагрузочное тестирование
- Интеграция с Telegram

## КРИТИЧЕСКИЕ МОМЕНТЫ:

1. **Минимальный простой**: Использовать blue-green deployment
2. **Сохранность данных**: Полное резервное копирование
3. **Откат**: План быстрого возврата на Render
4. **Мониторинг**: Логирование всех операций

## ВРЕМЕННЫЕ ОГРАНИЧЕНИЯ:
- Окно миграции: 2-4 часа
- Время простоя: < 30 минут
- Время отката: < 15 минут 