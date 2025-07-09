# API Documentation

## Обзор

Backend API для приложения Pax - сервиса поиска попутчиков.

## Базовый URL

```
https://api.pax-app.com/api/v1
```

## Аутентификация

### Telegram WebApp Authentication

```http
POST /auth/telegram/verify
```

**Request Body:**
```json
{
  "user": {
    "id": 123456789,
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "auth_date": 1640995200,
    "hash": "abc123..."
  }
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Регистрация пользователя

```http
POST /auth/register
```

**Request Body:**
```json
{
  "telegram_id": "123456789",
  "username": "johndoe",
  "full_name": "John Doe",
  "phone": "+79001234567",
  "city": "Moscow",
  "is_driver": false
}
```

## Поездки

### Создание поездки

```http
POST /rides/
```

**Request Body:**
```json
{
  "from_location": "Moscow",
  "to_location": "St. Petersburg",
  "date": "2024-01-15T10:00:00",
  "price": 1000.0,
  "seats": 3,
  "description": "Комфортная поездка"
}
```

### Поиск поездок

```http
GET /rides/search?from=Moscow&to=St. Petersburg&date=2024-01-15
```

**Query Parameters:**
- `from` - пункт отправления
- `to` - пункт назначения
- `date` - дата поездки (YYYY-MM-DD)
- `price_min` - минимальная цена
- `price_max` - максимальная цена
- `seats` - количество мест

### Получение деталей поездки

```http
GET /rides/{ride_id}
```

## Рейтинги

### Оставить отзыв

```http
POST /ratings/
```

**Request Body:**
```json
{
  "ride_id": 1,
  "rated_user_id": 2,
  "rating": 5,
  "comment": "Отличная поездка!"
}
```

## Уведомления

### Получение уведомлений

```http
GET /notifications/
```

### Отметить как прочитанное

```http
PUT /notifications/{notification_id}/read
```

## Модерация

### Подать жалобу

```http
POST /moderation/reports
```

**Request Body:**
```json
{
  "reported_user_id": 2,
  "ride_id": 1,
  "reason": "inappropriate_behavior",
  "description": "Описание проблемы"
}
```

## Коды ошибок

| Код | Описание |
|-----|----------|
| 400 | Bad Request - некорректные данные |
| 401 | Unauthorized - требуется аутентификация |
| 403 | Forbidden - недостаточно прав |
| 404 | Not Found - ресурс не найден |
| 409 | Conflict - конфликт данных |
| 422 | Unprocessable Entity - ошибка валидации |
| 500 | Internal Server Error - внутренняя ошибка сервера |

## Rate Limiting

API имеет ограничения на количество запросов:
- 100 запросов в час для аутентифицированных пользователей
- 10 запросов в час для неаутентифицированных пользователей

## Версионирование

API использует версионирование через URL:
- Текущая версия: `/api/v1`
- Будущие версии: `/api/v2`, `/api/v3` 