# 🚀 БЫСТРЫЙ СТАРТ МИГРАЦИИ: Render → Selectel

## ⚡ Экспресс-миграция (5 минут)

### 1. Проверка готовности
```bash
# Проверить подключение к серверу
ssh root@31.41.155.88 "echo 'Ready'"

# Сделать скрипты исполняемыми
chmod +x migration_scripts/*.sh
```

### 2. Запуск полной миграции
```bash
# Автоматическая миграция (2-4 часа)
./migration_scripts/run_migration.sh
```

### 3. Проверка результата
```bash
# Проверить статус
curl http://31.41.155.88:8000/health

# Проверить логи
tail -f migration.log
```

## 🔧 Поэтапная миграция

### Этап 1: Резервное копирование (15 минут)
```bash
./migration_scripts/backup_render_data.sh
```

### Этап 2: Подготовка сервера (30 минут)
```bash
./migration_scripts/prepare_selectel_server.sh
```

### Этап 3: Развертывание (60 минут)
```bash
./migration_scripts/deploy_to_selectel.sh
```

### Этап 4: Валидация (30 минут)
```bash
./migration_scripts/validate_migration.sh
```

## 🚨 Экстренные команды

### Быстрый откат (5 минут)
```bash
./migration_scripts/rollback.sh --force
```

### Проверка статуса
```bash
# Статус контейнеров
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose ps"

# Логи в реальном времени
ssh root@31.41.155.88 "cd /opt/pax-backend && docker-compose logs -f"

# Здоровье API
curl http://31.41.155.88:8000/health
```

## 📊 Мониторинг

### Ключевые URL:
- **Selectel API**: http://31.41.155.88:8000
- **Health Check**: http://31.41.155.88:8000/health
- **API Info**: http://31.41.155.88:8000/api/info

### Критические файлы:
- **Лог миграции**: `migration.log`
- **Отчет**: `migration_final_report.txt`
- **Валидация**: `migration_validation_report.txt`

## ⚠️ Важные моменты

### Перед миграцией:
- ✅ Убедитесь в доступности сервера
- ✅ Проверьте резервные копии
- ✅ Уведомите команду

### Во время миграции:
- ✅ Мониторьте логи
- ✅ Проверяйте здоровье API
- ✅ Будьте готовы к откату

### После миграции:
- ✅ Протестируйте все функции
- ✅ Настройте мониторинг
- ✅ Обновите документацию

## 📞 Контакты

- **Сервер**: ssh root@31.41.155.88
- **API**: http://31.41.155.88:8000
- **Логи**: `tail -f migration.log`
- **Откат**: `./migration_scripts/rollback.sh`

---

**🎯 Цель**: Миграция с минимальным простой (< 30 минут) и 100% сохранностью данных 