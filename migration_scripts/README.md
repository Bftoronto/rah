# МИГРАЦИЯ BACKEND: Render → Selectel

## 📋 Обзор

Полная миграция backend сервера с Render на Selectel с максимальной сохранностью данных и минимальными простоями.

## 🎯 Цели миграции

- ✅ 100% сохранность данных
- ✅ Минимальное время простоя (< 30 минут)
- ✅ Полная функциональность
- ✅ Идентичное поведение приложения
- ✅ Автоматизированный процесс

## 🏗️ Архитектура

### Текущая (Render):
- **Backend**: FastAPI + Uvicorn
- **База данных**: PostgreSQL (внешняя)
- **Кэширование**: Redis
- **Прокси**: Nginx
- **Контейнеризация**: Docker Compose

### Целевая (Selectel):
- **Сервер**: Ubuntu 22.04 LTS
- **IP**: 31.41.155.88
- **Порты**: 80, 443, 8000, 5432, 6379
- **Стек**: Идентичный Render

## 📁 Структура скриптов

```
migration_scripts/
├── README.md                    # Эта документация
├── run_migration.sh            # Главный скрипт миграции
├── backup_render_data.sh       # Резервное копирование с Render
├── prepare_selectel_server.sh  # Подготовка сервера Selectel
├── deploy_to_selectel.sh       # Развертывание на Selectel
├── validate_migration.sh       # Валидация миграции
└── rollback.sh                 # Скрипт отката
```

## 🚀 Быстрый старт

### 1. Подготовка

```bash
# Сделать скрипты исполняемыми
chmod +x migration_scripts/*.sh

# Проверить подключение к серверу
ssh root@31.41.155.88 "echo 'Connection test'"
```

### 2. Полная миграция

```bash
# Запуск полной миграции
./migration_scripts/run_migration.sh
```

### 3. Поэтапная миграция

```bash
# Только резервное копирование
./migration_scripts/backup_render_data.sh

# Только подготовка сервера
./migration_scripts/prepare_selectel_server.sh

# Только развертывание
./migration_scripts/deploy_to_selectel.sh

# Только валидация
./migration_scripts/validate_migration.sh
```

## 📊 Мониторинг

### Проверка статуса

```bash
# Проверка контейнеров
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose ps"

# Проверка логов
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose logs -f"

# Проверка здоровья API
curl http://31.41.155.88:8000/health
```

### Логи и отчеты

- `migration.log` - Основной лог миграции
- `migration_final_report.txt` - Финальный отчет
- `migration_validation_report.txt` - Отчет валидации
- `backups/` - Резервные копии

## 🔧 Опции скриптов

### run_migration.sh

```bash
# Полная миграция
./migration_scripts/run_migration.sh

# Пропустить резервное копирование
./migration_scripts/run_migration.sh --skip-backup

# Пропустить подготовку сервера
./migration_scripts/run_migration.sh --skip-prepare

# Только валидация
./migration_scripts/run_migration.sh --validate-only

# Справка
./migration_scripts/run_migration.sh --help
```

### rollback.sh

```bash
# Откат с подтверждением
./migration_scripts/rollback.sh

# Принудительный откат
./migration_scripts/rollback.sh --force

# Справка
./migration_scripts/rollback.sh --help
```

## ⚠️ Критические моменты

### Перед миграцией:
1. ✅ Убедитесь в доступности сервера Selectel
2. ✅ Проверьте все резервные копии
3. ✅ Уведомите команду о времени миграции
4. ✅ Подготовьте план отката

### Во время миграции:
1. ✅ Мониторьте логи в реальном времени
2. ✅ Проверяйте здоровье API каждые 5 минут
3. ✅ Готовьтесь к быстрому откату при проблемах

### После миграции:
1. ✅ Проведите полное тестирование всех функций
2. ✅ Настройте мониторинг и алерты
3. ✅ Обновите DNS записи (если необходимо)
4. ✅ Документируйте все изменения

## 🔄 План отката

### Быстрый откат (5 минут):

```bash
# Остановка Selectel и возврат к Render
./migration_scripts/rollback.sh --force
```

### Полный откат (15 минут):

1. Остановить сервисы на Selectel
2. Проверить доступность Render
3. Обновить конфигурации
4. Восстановить данные (если необходимо)

## 📈 Метрики успеха

### Временные рамки:
- **Общее время миграции**: 2-4 часа
- **Время простоя**: < 30 минут
- **Время отката**: < 15 минут

### Критерии успеха:
- ✅ Все API эндпоинты работают
- ✅ База данных доступна
- ✅ Redis кэширование работает
- ✅ Загрузка файлов функционирует
- ✅ Telegram Bot интеграция активна
- ✅ Производительность не хуже Render

## 🛠️ Устранение проблем

### Проблема: Не удается подключиться к серверу

```bash
# Проверка сети
ping 31.41.155.88

# Проверка SSH
ssh -v root@31.41.155.88

# Проверка firewall
ssh root@31.41.155.88 "ufw status"
```

### Проблема: Docker контейнеры не запускаются

```bash
# Проверка Docker
ssh root@31.41.155.88 "docker --version && docker-compose --version"

# Проверка логов
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose logs"

# Перезапуск сервисов
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose down && docker-compose up -d"
```

### Проблема: API недоступен

```bash
# Проверка портов
ssh root@31.41.155.88 "netstat -tlnp | grep :8000"

# Проверка контейнеров
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose ps"

# Проверка логов приложения
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose logs backend"
```

## 📞 Контакты и поддержка

### Серверная информация:
- **IP**: 31.41.155.88
- **SSH**: `ssh root@31.41.155.88`
- **API**: `http://31.41.155.88:8000`

### Мониторинг:
```bash
# Логи в реальном времени
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose logs -f"

# Статус сервисов
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose ps"

# Использование ресурсов
ssh root@31.41.155.88 "htop"
```

### Экстренные контакты:
- **Техническая поддержка**: [Контактная информация]
- **План отката**: `./migration_scripts/rollback.sh`
- **Логи**: `tail -f migration.log`

## 📚 Дополнительные ресурсы

- [План миграции](MIGRATION_PLAN.md)
- [Техническая спецификация](TECHNICAL_SPECIFICATION.md)
- [Документация API](backend/API_DOCUMENTATION.md)
- [Руководство по развертыванию](DEPLOYMENT_GUIDE.md)

---

**⚠️ ВАЖНО**: Всегда тестируйте миграцию в тестовой среде перед применением в продакшене! 