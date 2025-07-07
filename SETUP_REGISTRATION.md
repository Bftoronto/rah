# Настройка системы регистрации

## Обзор

Реализована полноценная система регистрации с единым профилем пользователя, которая поддерживает:

1. **Трехэтапную регистрацию**:
   - Пользовательское соглашение
   - Базовая информация
   - Водительские данные (опционально)

2. **Интеграцию с Telegram**:
   - Автоматическая верификация через Telegram Web App
   - Заполнение данных из Telegram профиля

3. **Гибкий профиль**:
   - Единый профиль для водителей и пассажиров
   - Возможность стать водителем в любой момент
   - История изменений профиля

## Структура базы данных

### Таблица `users`
- `id` - первичный ключ
- `telegram_id` - уникальный Telegram ID пользователя
- `phone` - номер телефона
- `full_name` - ФИО
- `birth_date` - дата рождения
- `city` - город проживания
- `avatar_url` - ссылка на аватар
- `is_active` - активность пользователя
- `is_verified` - верификация
- `is_driver` - статус водителя
- `privacy_policy_version` - версия принятого соглашения
- `privacy_policy_accepted` - принятие соглашения
- `privacy_policy_accepted_at` - дата принятия
- Водительские поля (опциональные):
  - `car_brand`, `car_model`, `car_year`, `car_color`
  - `driver_license_number`, `driver_license_photo_url`, `car_photo_url`
- Метаданные: `created_at`, `updated_at`, `rating`, `total_rides`, `cancelled_rides`
- `profile_history` - JSON с историей изменений

### Таблица `profile_change_logs`
- Логирование всех изменений профиля
- Поля: `user_id`, `field_name`, `old_value`, `new_value`, `changed_at`, `changed_by`

## Настройка окружения

### 1. Переменные окружения

Создайте файл `.env` в корне backend:

```env
# База данных
DATABASE_URL=postgresql://user:password@localhost/ridesharing

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username

# Безопасность
SECRET_KEY=your-secret-key-here

# Загрузка файлов
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# CORS
CORS_ORIGINS=["*"]

# Логирование
LOG_LEVEL=INFO
```

### 2. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 3. Инициализация базы данных

```bash
# Создание миграций
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

### 4. Запуск приложения

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Аутентификация и регистрация

- `POST /api/auth/telegram/verify` - Верификация пользователя через Telegram
- `POST /api/auth/register` - Регистрация нового пользователя
- `PUT /api/auth/profile/{user_id}` - Обновление профиля
- `POST /api/auth/privacy-policy/accept/{user_id}` - Принятие соглашения
- `GET /api/auth/privacy-policy` - Получение текста соглашения
- `GET /api/auth/profile/{user_id}` - Получение профиля
- `GET /api/auth/profile/{user_id}/history` - История изменений

## Фронтенд интеграция

### 1. Экраны регистрации

Созданы экраны в `assets/js/screens/registration.js`:
- `PrivacyPolicyScreen` - пользовательское соглашение
- `BasicInfoScreen` - базовая информация
- `DriverInfoScreen` - водительские данные

### 2. Обновление API

Добавлены методы в `assets/js/api.js`:
- `verifyTelegramUser()` - верификация Telegram
- `registerUser()` - регистрация
- `updateUserProfile()` - обновление профиля
- `getPrivacyPolicy()` - получение соглашения

### 3. Обновление состояния

Добавлено поле `registrationData` в `assets/js/state.js` для хранения данных регистрации.

## Безопасность

### 1. Верификация Telegram

- Проверка подписи данных от Telegram Web App
- Валидация времени авторизации (не старше 24 часов)
- Проверка обязательных полей

### 2. Валидация данных

- Проверка возраста (минимум 18 лет)
- Валидация номера телефона
- Проверка обязательных полей

### 3. Логирование

- Все изменения профиля логируются
- История изменений сохраняется в JSON и отдельной таблице
- Логирование ошибок и важных событий

## Тестирование

### 1. Тестирование API

```bash
# Запуск тестов
pytest tests/

# Тестирование конкретного модуля
pytest tests/test_auth.py
```

### 2. Тестирование фронтенда

Откройте приложение в браузере и проверьте:
- Загрузку экранов регистрации
- Валидацию форм
- Загрузку файлов
- Интеграцию с Telegram

## Развертывание

### 1. Docker

```bash
# Сборка образа
docker build -t ridesharing-backend .

# Запуск контейнера
docker run -p 8000:8000 --env-file .env ridesharing-backend
```

### 2. Production

- Настройте HTTPS
- Используйте production базу данных
- Настройте мониторинг и логирование
- Ограничьте CORS origins
- Настройте rate limiting

## Мониторинг

### 1. Health Check

- `GET /health` - проверка состояния приложения
- `GET /api/info` - информация об API

### 2. Логирование

- Все операции логируются
- Ошибки сохраняются с контекстом
- Настройте ротацию логов

## Поддержка

При возникновении проблем:

1. Проверьте логи приложения
2. Убедитесь в корректности переменных окружения
3. Проверьте подключение к базе данных
4. Убедитесь в корректности Telegram Bot Token

## Дальнейшее развитие

1. **Двухфакторная аутентификация**
2. **Верификация документов**
3. **Система рейтингов и отзывов**
4. **Уведомления через Telegram**
5. **Интеграция с платежными системами** 