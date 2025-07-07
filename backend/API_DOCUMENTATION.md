# API Документация

## Общая информация

Базовый URL: `http://localhost:8000`

Все запросы к защищенным эндпоинтам должны содержать заголовок авторизации:
```
Authorization: Bearer <token>
```

## Аутентификация

### POST /api/auth/login
Вход в систему через Telegram

**Параметры:**
```json
{
  "telegram_id": "123456789",
  "phone": "+79001234567",
  "full_name": "Иван Иванов",
  "birth_date": "1990-01-01",
  "city": "Москва"
}
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "telegram_id": "123456789",
    "full_name": "Иван Иванов",
    "phone": "+79001234567",
    "city": "Москва",
    "is_driver": false,
    "average_rating": 0.0
  }
}
```

## Поездки

### POST /api/rides/
Создание новой поездки

**Параметры:**
```json
{
  "from_location": "Москва",
  "to_location": "Санкт-Петербург",
  "date": "2024-01-20T10:00:00Z",
  "price": 1500.0,
  "seats": 3
}
```

### GET /api/rides/search
Поиск поездок с фильтрами

**Query параметры:**
- `from_location` (string) - место отправления
- `to_location` (string) - место назначения
- `date_from` (datetime) - дата от
- `date_to` (datetime) - дата до
- `max_price` (float) - максимальная цена
- `min_seats` (int) - минимальное количество мест
- `driver_id` (int) - ID водителя
- `status` (string) - статус поездки
- `limit` (int) - количество результатов (по умолчанию 50)
- `offset` (int) - смещение (по умолчанию 0)

### GET /api/rides/{ride_id}
Получение детальной информации о поездке

### POST /api/rides/{ride_id}/book
Бронирование поездки

### PUT /api/rides/{ride_id}/cancel
Отмена поездки

**Query параметры:**
- `is_driver` (boolean) - отмена водителем (по умолчанию false)

### PUT /api/rides/{ride_id}/complete
Завершение поездки

### GET /api/rides/user/me
Получение поездок текущего пользователя

**Query параметры:**
- `role` (string) - роль: all, driver, passenger (по умолчанию all)

### PUT /api/rides/{ride_id}
Обновление поездки

**Параметры:**
```json
{
  "from_location": "Москва",
  "to_location": "Санкт-Петербург",
  "date": "2024-01-20T10:00:00Z",
  "price": 1500.0,
  "seats": 3
}
```

### GET /api/rides/user/me/statistics
Получение статистики поездок пользователя

### DELETE /api/rides/{ride_id}
Удаление поездки (только водителем)

## Чат

### POST /api/chat/
Создание нового чата

**Параметры:**
```json
{
  "ride_id": 1,
  "user1_id": 1,
  "user2_id": 2
}
```

### GET /api/chat/
Получение всех чатов пользователя

**Query параметры:**
- `limit` (int) - количество чатов (по умолчанию 50)
- `offset` (int) - смещение (по умолчанию 0)

### GET /api/chat/{chat_id}/messages
Получение сообщений чата

**Query параметры:**
- `limit` (int) - количество сообщений (по умолчанию 50)
- `offset` (int) - смещение (по умолчанию 0)

### POST /api/chat/{chat_id}/send
Отправка сообщения в чат

**Параметры:**
```json
{
  "message": "Привет! Когда выезжаем?"
}
```

### PUT /api/chat/{chat_id}/read
Отметка сообщений чата как прочитанные

### DELETE /api/chat/messages/{message_id}
Удаление сообщения

### GET /api/chat/statistics
Получение статистики чатов пользователя

### GET /api/chat/unread/count
Получение количества непрочитанных сообщений

### GET /api/chat/{chat_id}/info
Получение информации о чате

### POST /api/chat/ride/{ride_id}/start
Создание чата для поездки

## WebSocket

### WebSocket /api/chat/ws/{user_id}
Real-time чат через WebSocket

**Подключение:**
```
ws://localhost:8000/api/chat/ws/1
```

**Отправка сообщения:**
```json
{
  "type": "message",
  "chat_id": 1,
  "message": "Привет!"
}
```

**Уведомление о наборе текста:**
```json
{
  "type": "typing",
  "chat_id": 1
}
```

**Отметка как прочитанное:**
```json
{
  "type": "read",
  "chat_id": 1
}
```

**Получение сообщений:**
```json
{
  "type": "new_message",
  "chat_id": 1,
  "message": {
    "id": 1,
    "message": "Привет!",
    "timestamp": "2024-01-15T10:00:00Z",
    "user_from_id": 1,
    "user_to_id": 2
  }
}
```

## Платежи (заглушка)

### POST /api/payment/process
Обработка платежа

**Параметры:**
```json
{
  "user_id": 1,
  "ride_id": 1,
  "amount": 1500.0
}
```

### GET /api/payment/history
Получение истории платежей пользователя

**Query параметры:**
- `limit` (int) - количество платежей (по умолчанию 50)
- `offset` (int) - смещение (по умолчанию 0)

### POST /api/payment/refund
Обработка возврата средств

**Query параметры:**
- `payment_id` (int) - ID платежа

### GET /api/payment/statistics
Получение статистики платежей пользователя

### GET /api/payment/{payment_id}
Получение информации о платеже

### POST /api/payment/ride/{ride_id}/pay
Оплата поездки

## Профиль

### GET /api/profile/me
Получение профиля текущего пользователя

### PUT /api/profile/me
Обновление профиля

**Параметры:**
```json
{
  "full_name": "Иван Иванов",
  "phone": "+79001234567",
  "city": "Москва",
  "birth_date": "1990-01-01",
  "car_brand": "Toyota",
  "car_model": "Camry",
  "car_year": 2020,
  "car_color": "Белый",
  "driver_license_number": "1234567890",
  "is_driver": true
}
```

### POST /api/profile/me/avatar
Загрузка аватара

### POST /api/profile/me/driver-license
Загрузка фото водительских прав

### POST /api/profile/me/car-photo
Загрузка фото автомобиля

## Рейтинги и отзывы

### POST /api/rating/
Создание отзыва

**Параметры:**
```json
{
  "target_user_id": 2,
  "ride_id": 1,
  "rating": 5,
  "review": "Отличный водитель, поездка прошла комфортно"
}
```

### GET /api/rating/user/{user_id}
Получение рейтингов пользователя

**Query параметры:**
- `limit` (int) - количество отзывов (по умолчанию 50)
- `offset` (int) - смещение (по умолчанию 0)

### GET /api/rating/ride/{ride_id}
Получение отзывов о поездке

**Query параметры:**
- `limit` (int) - количество отзывов (по умолчанию 50)
- `offset` (int) - смещение (по умолчанию 0)

### GET /api/rating/statistics
Получение статистики рейтингов

### GET /api/rating/top
Получение топ пользователей по рейтингу

## Модерация

### POST /api/moderation/report
Подача жалобы

**Параметры:**
```json
{
  "target_type": "user",
  "target_id": 2,
  "reason": "spam",
  "description": "Отправляет спам сообщения"
}
```

### GET /api/moderation/reports
Получение жалоб (для модераторов)

### PUT /api/moderation/reports/{report_id}
Обработка жалобы (для модераторов)

## Уведомления

### GET /api/notifications/
Получение уведомлений пользователя

### PUT /api/notifications/{notification_id}/read
Отметка уведомления как прочитанное

### DELETE /api/notifications/{notification_id}
Удаление уведомления

## Загрузка файлов

### POST /api/upload/avatar
Загрузка аватара

### POST /api/upload/driver-license
Загрузка фото водительских прав

### POST /api/upload/car-photo
Загрузка фото автомобиля

## Статусы поездок

- `active` - активная поездка
- `booked` - забронированная поездка
- `completed` - завершенная поездка
- `cancelled` - отмененная поездка
- `expired` - просроченная поездка
- `deleted` - удаленная поездка

## Статусы платежей

- `pending` - ожидает обработки
- `completed` - завершен
- `failed` - неудачный
- `refunded` - возвращен

## Коды ошибок

- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `422` - Ошибка валидации
- `500` - Внутренняя ошибка сервера

## Примеры использования

### Создание поездки
```bash
curl -X POST "http://localhost:8000/api/rides/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from_location": "Москва",
    "to_location": "Санкт-Петербург",
    "date": "2024-01-20T10:00:00Z",
    "price": 1500.0,
    "seats": 3
  }'
```

### Поиск поездок
```bash
curl -X GET "http://localhost:8000/api/rides/search?from_location=Москва&max_price=2000&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Отправка сообщения
```bash
curl -X POST "http://localhost:8000/api/chat/1/send" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привет! Когда выезжаем?"
  }'
``` 