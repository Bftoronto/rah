# Система уведомлений PAX

## Обзор

Система уведомлений PAX обеспечивает надежную доставку уведомлений пользователям через Telegram Bot API. Система поддерживает различные типы уведомлений, настройки пользователей, логирование и автоматические напоминания.

## Архитектура

### Компоненты

1. **NotificationService** - основной сервис для отправки уведомлений
2. **API Endpoints** - REST API для управления уведомлениями
3. **Database Models** - модели для логов и настроек
4. **Frontend Components** - интерфейс настроек уведомлений

### Технологии

- **Backend**: FastAPI, SQLAlchemy, aiohttp
- **Frontend**: Vanilla JavaScript, CSS3
- **Database**: SQLite/PostgreSQL
- **External API**: Telegram Bot API

## Типы уведомлений

### 1. Уведомления о поездках

- **new_ride** - новая поездка по маршруту пользователя
- **ride_reminder** - напоминание о поездке за час
- **ride_cancelled** - отмена поездки
- **booking_confirmed** - подтверждение бронирования
- **new_passenger** - новый пассажир забронировал место

### 2. Системные уведомления

- **info** - информационные сообщения
- **success** - успешные операции
- **warning** - предупреждения
- **error** - ошибки
- **security** - уведомления безопасности

## API Endpoints

### Отправка уведомлений

```http
POST /api/notifications/send/ride
POST /api/notifications/send/system
POST /api/notifications/send/bulk
```

### Управление настройками

```http
GET /api/notifications/settings/{user_id}
PUT /api/notifications/settings/{user_id}
```

### Тестирование и мониторинг

```http
GET /api/notifications/test/{user_id}
GET /api/notifications/status
POST /api/notifications/reminders/send
```

## Настройки пользователя

### Типы уведомлений

- `ride_notifications` - уведомления о поездках
- `system_notifications` - системные уведомления
- `reminder_notifications` - напоминания
- `marketing_notifications` - маркетинговые уведомления

### Тихие часы

- `quiet_hours_start` - начало тихих часов (HH:MM)
- `quiet_hours_end` - конец тихих часов (HH:MM)

## Логирование

### NotificationLog

- `id` - уникальный идентификатор
- `user_id` - ID пользователя
- `notification_type` - тип уведомления
- `title` - заголовок
- `message` - текст сообщения
- `sent_at` - время отправки
- `success` - успешность отправки
- `error_message` - сообщение об ошибке
- `telegram_response` - ответ от Telegram API

## Безопасность

### Валидация

- Проверка существования пользователя
- Валидация типов уведомлений
- Проверка настроек пользователя
- Ограничение массовой рассылки (максимум 1000 пользователей)

### Обработка ошибок

- Логирование всех ошибок
- Graceful degradation при недоступности Telegram API
- Retry механизм для критических уведомлений

## Производительность

### Оптимизации

- Асинхронная отправка через BackgroundTasks
- Переиспользование HTTP сессий
- Индексы в базе данных
- Ограничение размера сообщений

### Мониторинг

- Статистика успешности отправки
- Время отклика API
- Количество ошибок
- Использование ресурсов

## Развертывание

### Требования

1. **Telegram Bot Token** - токен бота для отправки уведомлений
2. **Database** - база данных с таблицами уведомлений
3. **Environment Variables**:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   ```

### Миграции

```bash
# Применение миграций
alembic upgrade head

# Создание новой миграции
alembic revision --autogenerate -m "description"
```

### Запуск

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn app.main:app --reload
```

## Использование

### Отправка уведомления о поездке

```python
from app.services.notification_service import notification_service

# Отправка уведомления
await notification_service.send_ride_notification(
    user=user,
    ride_data={
        "id": ride.id,
        "from": "Москва",
        "to": "Санкт-Петербург",
        "date": "25.12.2024",
        "time": "10:00",
        "price": "1500",
        "driver_name": "Иван Иванов"
    },
    notification_type="new_ride",
    db=db
)
```

### Отправка системного уведомления

```python
await notification_service.send_system_notification(
    user=user,
    title="Обновление приложения",
    message="Доступна новая версия приложения",
    notification_type="info",
    db=db
)
```

### Массовая рассылка

```python
users = [user1, user2, user3]
results = await notification_service.send_bulk_notification(
    users=users,
    title="Важное уведомление",
    message="Система будет недоступна с 2:00 до 4:00",
    notification_type="warning",
    db=db
)
```

## Настройка Telegram Bot

### 1. Создание бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Получите токен бота

### 2. Настройка Webhook (опционально)

```python
# Установка webhook
await bot.set_webhook(url="https://your-domain.com/webhook")
```

### 3. Обработка callback queries

```python
# Обработка нажатий на кнопки
@router.post("/webhook")
async def telegram_webhook(update: dict):
    if "callback_query" in update:
        callback_data = update["callback_query"]["data"]
        # Обработка callback_data
```

## Тестирование

### Unit тесты

```bash
# Запуск тестов
pytest tests/test_notifications.py

# Покрытие кода
pytest --cov=app/services/notification_service
```

### Интеграционные тесты

```bash
# Тест отправки уведомления
curl -X GET "http://localhost:8000/api/notifications/test/1"

# Проверка статуса
curl -X GET "http://localhost:8000/api/notifications/status"
```

## Мониторинг и аналитика

### Метрики

- Количество отправленных уведомлений
- Процент успешной доставки
- Время отклика Telegram API
- Популярные типы уведомлений
- Активность пользователей

### Алерты

- Высокий процент ошибок (>5%)
- Долгое время отклика (>5 секунд)
- Недоступность Telegram API
- Превышение лимитов API

## Troubleshooting

### Частые проблемы

1. **Ошибка 401 Unauthorized**
   - Проверьте правильность токена бота
   - Убедитесь, что бот активен

2. **Ошибка 403 Forbidden**
   - Пользователь заблокировал бота
   - Проверьте права бота

3. **Ошибка 429 Too Many Requests**
   - Превышен лимит запросов к Telegram API
   - Добавьте задержки между запросами

4. **Уведомления не доходят**
   - Проверьте настройки пользователя
   - Убедитесь, что пользователь не в тихих часах
   - Проверьте логи на наличие ошибок

### Логи

```bash
# Просмотр логов
tail -f logs/app.log | grep notification

# Поиск ошибок
grep "ERROR.*notification" logs/app.log
```

## Будущие улучшения

### Планируемые функции

1. **Push-уведомления** - интеграция с Firebase
2. **Email уведомления** - резервный канал доставки
3. **SMS уведомления** - для критически важных сообщений
4. **Шаблоны уведомлений** - динамические шаблоны
5. **A/B тестирование** - тестирование эффективности
6. **Персонализация** - адаптация под пользователя
7. **Аналитика** - детальная статистика
8. **Модерация** - проверка содержимого уведомлений

### Оптимизации

1. **Кэширование** - кэш настроек пользователей
2. **Очереди** - Redis для очередей уведомлений
3. **Кластеризация** - горизонтальное масштабирование
4. **CDN** - для статических ресурсов
5. **Rate Limiting** - защита от спама 