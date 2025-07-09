#!/bin/bash

# Скрипт развертывания на Selectel сервер
# Выполняется на сервере: ssh root@31.41.155.88

set -e

echo "🚀 Начинаем развертывание на Selectel..."

# Переменные
SELECTEL_SERVER="31.41.155.88"
APP_DIR="/opt/pax-backend"
BACKUP_DIR="./backups"

# Проверка наличия бэкапов
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Директория с бэкапами не найдена: $BACKUP_DIR"
    echo "Сначала выполните: ./migration_scripts/backup_render_data.sh"
    exit 1
fi

# Находим последний бэкап
LATEST_BACKUP=$(ls -t "$BACKUP_DIR" | head -1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ Бэкапы не найдены в $BACKUP_DIR"
    exit 1
fi

BACKUP_PATH="$BACKUP_DIR/$LATEST_BACKUP"
echo "📁 Используем бэкап: $BACKUP_PATH"

# 1. Копирование файлов на сервер
echo "📤 Копирование файлов на сервер..."
scp -r "$BACKUP_PATH" root@$SELECTEL_SERVER:/tmp/

# 2. Подключение к серверу и развертывание
ssh root@$SELECTEL_SERVER << 'EOF'

set -e

echo "🔧 Начинаем развертывание на сервере..."

# Переменные
APP_DIR="/opt/pax-backend"
BACKUP_PATH="/tmp/$(ls -t /tmp | grep backup | head -1)"

if [ ! -d "$BACKUP_PATH" ]; then
    echo "❌ Бэкап не найден в /tmp"
    exit 1
fi

echo "📁 Используем бэкап: $BACKUP_PATH"

# Остановка существующих контейнеров
echo "🛑 Остановка существующих контейнеров..."
cd $APP_DIR
if [ -f "docker-compose.yml" ]; then
    docker-compose down || true
fi

# Очистка директории
echo "🧹 Очистка директории приложения..."
rm -rf $APP_DIR/*
mkdir -p $APP_DIR/uploads
mkdir -p $APP_DIR/ssl
mkdir -p $APP_DIR/logs

# Распаковка кода
echo "📦 Распаковка кода..."
tar -xzf "$BACKUP_PATH/code_backup.tar.gz" -C $APP_DIR --strip-components=1

# Распаковка uploads (если есть)
if [ -f "$BACKUP_PATH/uploads_backup.tar.gz" ]; then
    echo "📁 Распаковка uploads..."
    tar -xzf "$BACKUP_PATH/uploads_backup.tar.gz" -C $APP_DIR --strip-components=2
fi

# Настройка прав доступа
echo "🔐 Настройка прав доступа..."
chown -R root:root $APP_DIR
chmod -R 755 $APP_DIR
chmod -R 777 $APP_DIR/uploads
chmod -R 755 $APP_DIR/ssl

# Создание .env файла
echo "⚙️ Создание .env файла..."
cat > $APP_DIR/.env << 'ENVEOF'
# База данных
DATABASE_URL=postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain

# Telegram Bot
TELEGRAM_BOT_TOKEN=8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA
TELEGRAM_BOT_USERNAME=paxdemobot

# Безопасность
SECRET_KEY=8f3b2c1e-4a5d-11ee-be56-0242ac120002
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Настройки приложения
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Загрузка файлов
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif

# CORS
CORS_ORIGINS=https://web.telegram.org,https://t.me,https://frabjous-florentine-c506b0.netlify.app,https://31.41.155.88

# Redis
REDIS_URL=redis://localhost:6379
ENVEOF

# Обновление docker-compose.yml для Selectel
echo "🐳 Обновление docker-compose.yml..."
cat > $APP_DIR/docker-compose.yml << 'COMPOSEEOF'
services:
  # База данных PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ridesharing
      POSTGRES_USER: rideshare_user
      POSTGRES_PASSWORD: rideshare_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rideshare_user -d ridesharing"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis для кэширования
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend FastAPI
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain
      - REDIS_URL=redis://redis:6379
      - TELEGRAM_BOT_TOKEN=8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA
      - SECRET_KEY=8f3b2c1e-4a5d-11ee-be56-0242ac120002
      - DEBUG=false
      - ENVIRONMENT=production
    volumes:
      - ./app:/app/app
      - ./uploads:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  # Nginx для проксирования и статики
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./uploads:/usr/share/nginx/html/uploads
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
COMPOSEEOF

# Сборка и запуск контейнеров
echo "🔨 Сборка контейнеров..."
cd $APP_DIR
docker-compose build

echo "🚀 Запуск контейнеров..."
docker-compose up -d

# Ожидание запуска сервисов
echo "⏳ Ожидание запуска сервисов..."
sleep 30

# Проверка статуса контейнеров
echo "🔍 Проверка статуса контейнеров..."
docker-compose ps

# Проверка здоровья API
echo "🏥 Проверка здоровья API..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API доступен"
        break
    else
        echo "⏳ Попытка $i/10..."
        sleep 10
    fi
done

# Восстановление базы данных (если нужно)
if [ -f "$BACKUP_PATH/database_backup.sql" ]; then
    echo "🗄️ Восстановление базы данных..."
    # Здесь можно добавить логику восстановления БД
    echo "⚠️ Восстановление БД требует ручного вмешательства"
fi

# Очистка временных файлов
echo "🧹 Очистка временных файлов..."
rm -rf /tmp/*backup*

echo "✅ Развертывание завершено!"
echo "📊 Статус сервисов:"
docker-compose ps

echo "🌐 API доступен по адресу: http://31.41.155.88:8000"
echo "📋 Логи: docker-compose logs -f"

EOF

echo "✅ Развертывание на Selectel завершено!"
echo "🔗 Проверьте доступность: http://31.41.155.88:8000/health" 