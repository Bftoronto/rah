# PAX - Поездки с попутчиками

## 🚀 Готово к продакшену

**Проект полностью готов к развертыванию на продакшен сервер.**

Все необходимые скрипты автоматизации созданы для быстрого и безопасного развертывания.

## 📱 Telegram Mini App

Приложение также доступно как Telegram Mini App с полной интеграцией:
- Автоматическая авторизация через Telegram
- Push-уведомления
- Нативная интеграция с мессенджером

## 🏗️ Архитектура

### Frontend
- **Технологии:** Vanilla JavaScript, HTML5, CSS3
- **Архитектура:** SPA (Single Page Application)
- **Стили:** Модульная CSS архитектура
- **Адаптивность:** Полная поддержка мобильных устройств
- **Безопасность:** Защита от XSS атак, валидация данных

### Backend
- **Фреймворк:** FastAPI (Python)
- **База данных:** PostgreSQL с оптимизированными индексами
- **Аутентификация:** JWT + Telegram Login
- **API:** RESTful API с полной документацией
- **Безопасность:** Валидация входных данных, защита от SQL-инъекций

## 🚀 Быстрый старт

### Развертывание на продакшен сервер

#### 1. Подготовка сервера
```bash
# Убедитесь, что у вас есть:
# - IP адрес сервера
# - SSH ключ для доступа
# - Домен (опционально, для SSL)
# - Telegram Bot Token
```

#### 2. Развертывание приложения
```bash
# Развертывание на сервер
./deploy_production.sh <server_ip> [ssh_key_path]

# Пример:
./deploy_production.sh 192.168.1.100 ~/.ssh/id_rsa
```

#### 3. Настройка SSL и домена (рекомендуется)
```bash
# Настройка SSL сертификата
./setup_ssl_domain.sh <server_ip> <domain> [ssh_key_path]

# Пример:
./setup_ssl_domain.sh 192.168.1.100 myapp.com ~/.ssh/id_rsa
```

#### 4. Настройка Telegram бота
```bash
# Настройка Telegram бота
./setup_telegram_bot.sh <server_ip> <bot_token> <domain> [ssh_key_path]

# Пример:
./setup_telegram_bot.sh 192.168.1.100 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz myapp.com ~/.ssh/id_rsa
```

## 📊 Основные функции

### Для пассажиров
- 🔍 Поиск поездок по маршруту и дате
- 🪙 Бронирование мест (оплата наличными или переводом)
- ⭐ Система рейтингов и отзывов
- 💬 Встроенный чат с водителем
- 🔔 Push-уведомления о статусе поездки

### Для водителей
- 🚗 Создание поездок с указанием маршрута
- 👥 Управление пассажирами и местами
- 💵 Получение оплаты напрямую от пассажира (наличные/перевод)
- 📊 Статистика поездок
- 🛡️ Система модерации и безопасности

## 💵 Механизм расчетов

**Все расчеты осуществляются напрямую между пассажиром и водителем:**

<div aria-label="Способы оплаты" style="font-size:16px;">
  <span role="img" aria-label="наличные">💵</span> Наличный расчет <span style="color:#bbb;">|</span> <span role="img" aria-label="перевод на карту">💳</span> Перевод на карту
</div>
<span style="font-size:13px;color:#888;">Онлайн-оплата через приложение отсутствует. Платформа не хранит и не обрабатывает платежные данные.</span>

## 🔧 Технические особенности

### Безопасность
- JWT токены для аутентификации
- Верификация Telegram Login
- Защита от SQL-инъекций и XSS атак
- Валидация всех входных данных
- Безопасная обработка HTML контента

### Производительность
- Кэширование с Redis
- Оптимизированные SQL-запросы с индексами
- Сжатие статических файлов
- CDN для медиа-контента
- Оптимизированная работа с localStorage

### Масштабируемость
- Микросервисная архитектура
- Горизонтальное масштабирование
- Балансировка нагрузки
- Мониторинг и логирование

## 📈 Метрики и аналитика

- Количество активных пользователей
- Статистика поездок и бронирований
- Финансовые показатели (только агрегированные, без онлайн-оплаты)
- Географическое распределение

## 🛠️ Разработка

### Структура проекта
```
├── assets/          # Frontend ресурсы
│   ├── css/        # Стили
│   └── js/         # JavaScript модули
├── backend/         # Python FastAPI backend
│   ├── app/        # Основной код приложения
│   ├── migrations/ # Миграции базы данных
│   └── tests/      # Тесты
├── design/          # Дизайн-макеты
└── docs/           # Документация
```

### API Документация
Полная документация API доступна по адресу: `/docs` (Swagger UI)

## 🚀 Деплой

### Автоматическое развертывание

Проект готов к прямому развертыванию на продакшен сервер без локальной разработки.

#### Требования к серверу:
- **OS:** Ubuntu 20.04+ или Debian 11+
- **RAM:** Минимум 2GB (рекомендуется 4GB+)
- **Storage:** Минимум 20GB
- **Network:** Статический IP адрес

#### Процесс развертывания:

1. **Развертывание приложения:**
   ```bash
   ./deploy_production.sh <server_ip> [ssh_key_path]
   ```

2. **Настройка SSL (рекомендуется):**
   ```bash
   ./setup_ssl_domain.sh <server_ip> <domain> [ssh_key_path]
   ```

3. **Настройка Telegram бота:**
   ```bash
   ./setup_telegram_bot.sh <server_ip> <bot_token> <domain> [ssh_key_path]
   ```

#### Что устанавливается автоматически:
- ✅ Python 3.8+
- ✅ PostgreSQL 13+
- ✅ Redis 6+
- ✅ Nginx
- ✅ SSL сертификаты (Let's Encrypt)
- ✅ Systemd сервисы
- ✅ Автоматические бэкапы
- ✅ Мониторинг и логирование

## 🚨 Устранение неполадок

### Проблема с Pydantic BaseSettings

Если приложение не запускается с ошибкой:
```
pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package.
```

**Решение:**
```bash
# Автоматическое исправление
./fix_pydantic_issue.sh <server_ip> [ssh_key_path]

# Или ручное исправление
ssh root@<server_ip>
cd /opt/pax-app/backend
source venv/bin/activate
pip install pydantic-settings==2.1.0
systemctl restart pax-backend
```

Подробная инструкция: [PYDANTIC_FIX_INSTRUCTIONS.md](PYDANTIC_FIX_INSTRUCTIONS.md)

### Проблема с импортами конфигурации

Если приложение не запускается с ошибкой:
```
ModuleNotFoundError: No module named 'app.config_simple'
```

**Решение:**
```bash
# Автоматическое исправление
./fix_config_imports.sh <server_ip> [ssh_key_path]

# Или ручное исправление
ssh root@<server_ip>
cd /opt/pax-app/backend
sed -i 's/from \.config_simple import settings/from .config.settings import settings/' app/database.py
sed -i 's/from \.\.config_simple import settings/from ..config.settings import settings/' app/services/notification_service.py
sed -i 's/from \.\.config_simple import settings/from ..config.settings import settings/' app/services/moderation_service.py
systemctl restart pax-backend
```

Подробная инструкция: [CONFIG_IMPORTS_FIX_INSTRUCTIONS.md](CONFIG_IMPORTS_FIX_INSTRUCTIONS.md)

## 🔒 Готовность к продакшену

### v6.2 - Полная подготовка к продакшену
- ✅ **Автоматическое развертывание**: Созданы скрипты для прямого развертывания на сервер
- ✅ **SSL сертификаты**: Автоматическая настройка Let's Encrypt
- ✅ **Telegram интеграция**: Автоматическая настройка webhook и бота
- ✅ **Мониторинг**: Система мониторинга и обслуживания сервера
- ✅ **Безопасность**: Настроены firewall, валидация, шифрование
- ✅ **Производительность**: Оптимизированы запросы, кэширование, индексы
- ✅ **Масштабируемость**: Готова архитектура для горизонтального масштабирования
- ✅ **Документация**: Полная документация по развертыванию и обслуживанию
- ✅ **Исправления**: Решена проблема с Pydantic BaseSettings


## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

---

**Версия:** v6.2
**Последнее обновление:** 9 Июля  
**Статус:** Полностью готов к продакшену с автоматическим развертыванием