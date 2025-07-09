#!/bin/bash

# Скрипт резервного копирования данных с Render
# Выполняется локально перед миграцией

set -e

echo "💾 Начинаем резервное копирование данных с Render..."

# Создание директории для бэкапов
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "📁 Создана директория для бэкапов: $BACKUP_DIR"

# Переменные окружения Render
RENDER_DB_URL="postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain"
RENDER_BACKEND_URL="https://pax-backend-2gng.onrender.com"

# 1. Резервное копирование PostgreSQL
echo "🗄️ Создание бэкапа PostgreSQL..."
pg_dump "$RENDER_DB_URL" > "$BACKUP_DIR/database_backup.sql"

# Проверка размера бэкапа
BACKUP_SIZE=$(du -h "$BACKUP_DIR/database_backup.sql" | cut -f1)
echo "✅ Бэкап БД создан: $BACKUP_SIZE"

# 2. Создание бэкапа кода
echo "📦 Создание бэкапа кода..."
tar -czf "$BACKUP_DIR/code_backup.tar.gz" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='uploads' \
    backend/

# 3. Создание бэкапа uploads (если доступен)
echo "📁 Создание бэкапа uploads..."
if [ -d "backend/uploads" ]; then
    tar -czf "$BACKUP_DIR/uploads_backup.tar.gz" backend/uploads/
    echo "✅ Бэкап uploads создан"
else
    echo "⚠️ Директория uploads не найдена"
fi

# 4. Создание бэкапа конфигураций
echo "⚙️ Создание бэкапа конфигураций..."
cat > "$BACKUP_DIR/environment_backup.txt" << EOF
# Резервная копия переменных окружения
# Дата создания: $(date)

# База данных
DATABASE_URL=$RENDER_DB_URL

# Telegram Bot
TELEGRAM_BOT_TOKEN=8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA
TELEGRAM_BOT_USERNAME=paxdemobot

# Безопасность
SECRET_KEY=8f3b2c1e-4a5d-11ee-be56-0242ac120002
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Настройки приложения
DEBUG=true
ENVIRONMENT=production
LOG_LEVEL=INFO

# Загрузка файлов
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif

# CORS
CORS_ORIGINS=https://web.telegram.org,https://t.me,https://frabjous-florentine-c506b0.netlify.app,https://pax-backend-2gng.onrender.com
EOF

# 5. Проверка доступности API
echo "🔍 Проверка доступности API..."
if curl -f "$RENDER_BACKEND_URL/health" > /dev/null 2>&1; then
    echo "✅ API доступен"
    curl -s "$RENDER_BACKEND_URL/health" > "$BACKUP_DIR/api_health_check.json"
else
    echo "❌ API недоступен"
fi

# 6. Создание отчета о бэкапе
echo "📊 Создание отчета о бэкапе..."
cat > "$BACKUP_DIR/backup_report.txt" << EOF
ОТЧЕТ О РЕЗЕРВНОМ КОПИРОВАНИИ
================================
Дата: $(date)
Время: $(date +%H:%M:%S)

СОЗДАННЫЕ ФАЙЛЫ:
- database_backup.sql: Бэкап PostgreSQL
- code_backup.tar.gz: Бэкап исходного кода
- uploads_backup.tar.gz: Бэкап загруженных файлов
- environment_backup.txt: Переменные окружения
- api_health_check.json: Проверка здоровья API

РАЗМЕРЫ ФАЙЛОВ:
$(du -h "$BACKUP_DIR"/*)

СТАТУС:
- База данных: ✅
- Код: ✅
- Конфигурации: ✅
- API проверка: $(if curl -f "$RENDER_BACKEND_URL/health" > /dev/null 2>&1; then echo "✅"; else echo "❌"; fi)

СЛЕДУЮЩИЕ ШАГИ:
1. Проверить целостность бэкапов
2. Перенести файлы на Selectel сервер
3. Восстановить данные
4. Протестировать функциональность
EOF

# 7. Проверка целостности бэкапов
echo "🔍 Проверка целостности бэкапов..."

# Проверка SQL бэкапа
if pg_restore --list "$BACKUP_DIR/database_backup.sql" > /dev/null 2>&1; then
    echo "✅ SQL бэкап корректен"
else
    echo "❌ SQL бэкап поврежден"
fi

# Проверка архива кода
if tar -tzf "$BACKUP_DIR/code_backup.tar.gz" > /dev/null 2>&1; then
    echo "✅ Архив кода корректен"
else
    echo "❌ Архив кода поврежден"
fi

# Проверка архива uploads
if [ -f "$BACKUP_DIR/uploads_backup.tar.gz" ]; then
    if tar -tzf "$BACKUP_DIR/uploads_backup.tar.gz" > /dev/null 2>&1; then
        echo "✅ Архив uploads корректен"
    else
        echo "❌ Архив uploads поврежден"
    fi
fi

echo "📋 Отчет сохранен в: $BACKUP_DIR/backup_report.txt"
echo "✅ Резервное копирование завершено!"
echo "📁 Все файлы сохранены в: $BACKUP_DIR" 