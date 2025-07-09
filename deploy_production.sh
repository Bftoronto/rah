#!/bin/bash

# Скрипт развертывания на продакшен сервер
# Использование: ./deploy_production.sh

set -e  # Остановка при ошибке

echo "🚀 Развертывание PAX на продакшен сервер"
echo "=========================================="

# Проверка аргументов
if [ $# -eq 0 ]; then
    echo "❌ Ошибка: Укажите IP адрес сервера"
    echo "Использование: ./deploy_production.sh <server_ip> [ssh_key_path]"
    echo "Пример: ./deploy_production.sh 192.168.1.100 ~/.ssh/id_rsa"
    exit 1
fi

SERVER_IP=$1
SSH_KEY=${2:-"~/.ssh/id_rsa"}
SSH_USER="root"

echo "📋 Параметры развертывания:"
echo "   Сервер: $SERVER_IP"
echo "   SSH ключ: $SSH_KEY"
echo "   Пользователь: $SSH_USER"

# Проверка подключения к серверу
echo "🔍 Проверка подключения к серверу..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$SSH_USER@$SERVER_IP" exit 2>/dev/null; then
    echo "❌ Не удалось подключиться к серверу"
    echo "Проверьте:"
    echo "  - IP адрес сервера"
    echo "  - SSH ключ"
    echo "  - Доступ к серверу"
    exit 1
fi

echo "✅ Подключение к серверу успешно"

# Создание временного архива
echo "📦 Подготовка файлов для развертывания..."
TEMP_ARCHIVE="pax_deploy_$(date +%Y%m%d_%H%M%S).tar.gz"

# Исключаем ненужные файлы
tar --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='backups' \
    --exclude='uploads' \
    --exclude='logs' \
    --exclude='*.log' \
    --exclude='test_*.html' \
    --exclude='diagnose_*.py' \
    --exclude='check_*.py' \
    --exclude='fix_*.py' \
    --exclude='emergency_*.py' \
    --exclude='final_*.py' \
    -czf "$TEMP_ARCHIVE" .

echo "📤 Загрузка файлов на сервер..."
scp -i "$SSH_KEY" "$TEMP_ARCHIVE" "$SSH_USER@$SERVER_IP:/tmp/"

# Очистка временного архива
rm "$TEMP_ARCHIVE"

echo "🔧 Настройка сервера..."
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << 'EOF'
set -e

echo "📋 Обновление системы..."
apt update && apt upgrade -y

echo "📦 Установка необходимых пакетов..."
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib redis-server certbot python3-certbot-nginx

echo "🔧 Настройка PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

# Создание пользователя и базы данных
sudo -u postgres psql << 'PSQL'
CREATE USER pax_user WITH PASSWORD 'pax_secure_password_2024';
CREATE DATABASE pax_db OWNER pax_user;
GRANT ALL PRIVILEGES ON DATABASE pax_db TO pax_user;
\q
PSQL

echo "🔧 Настройка Redis..."
systemctl start redis-server
systemctl enable redis-server

echo "📁 Распаковка файлов..."
cd /opt
tar -xzf /tmp/pax_deploy_*.tar.gz -C /opt/
mv pax-* pax-app
cd pax-app

echo "🐍 Настройка Python окружения..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pydantic-settings==2.1.0

echo "🔧 Создание .env файла..."
cat > .env << 'ENV'
# Основные настройки
ENVIRONMENT=production
DEBUG=false
APP_NAME=Pax Backend
APP_VERSION=1.0.0

# База данных
DATABASE_URL=postgresql://pax_user:pax_secure_password_2024@localhost:5432/pax_db

# Безопасность
SECRET_KEY=your-super-secret-production-key-change-this-immediately
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram (ЗАМЕНИТЕ НА ВАШИ ДАННЫЕ)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here

# CORS
CORS_ORIGINS=https://your-domain.com,https://web.telegram.org

# Логирование
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Мониторинг
ENABLE_METRICS=true
METRICS_PORT=8001

# Redis
REDIS_URL=redis://localhost:6379

# Файлы
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760

# Уведомления
NOTIFICATION_QUEUE_SIZE=1000

# Модерация
AUTO_MODERATION=true
MODERATION_THRESHOLD=0.7
ENV

echo "📁 Создание необходимых директорий..."
mkdir -p logs uploads
chmod 755 logs uploads

echo "🔧 Применение миграций..."
source venv/bin/activate
alembic upgrade head

echo "🔧 Настройка systemd сервиса..."
cat > /etc/systemd/system/pax-backend.service << 'SERVICE'
[Unit]
Description=Pax Backend API
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/pax-app/backend
Environment=PATH=/opt/pax-app/backend/venv/bin
ExecStart=/opt/pax-app/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

echo "🔧 Настройка Nginx..."
cat > /etc/nginx/sites-available/pax-app << 'NGINX'
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root /opt/pax-app;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Кэширование статических файлов
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
    
    # Metrics (только для localhost)
    location /metrics {
        allow 127.0.0.1;
        deny all;
        proxy_pass http://127.0.0.1:8000;
    }
    
    # Безопасность
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
NGINX

# Активация конфигурации Nginx
ln -sf /etc/nginx/sites-available/pax-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

echo "🔧 Запуск сервисов..."
systemctl daemon-reload
systemctl enable pax-backend
systemctl start pax-backend

echo "⏳ Ожидание запуска сервисов..."
sleep 10

echo "📊 Проверка статуса сервисов..."
systemctl status pax-backend --no-pager
systemctl status nginx --no-pager
systemctl status postgresql --no-pager
systemctl status redis-server --no-pager

echo "🔍 Проверка доступности API..."
curl -f http://localhost:8000/health || echo "❌ API недоступен"

echo "🧹 Очистка временных файлов..."
rm -f /tmp/pax_deploy_*.tar.gz

EOF

echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "============================="
echo ""
echo "📱 Frontend: http://$SERVER_IP"
echo "🔧 Backend API: http://$SERVER_IP/api"
echo "📚 API документация: http://$SERVER_IP/api/docs"
echo "📊 Health Check: http://$SERVER_IP/health"
echo ""
echo "⚠️  ВАЖНЫЕ СЛЕДУЮЩИЕ ШАГИ:"
echo "1. Отредактируйте /opt/pax-app/backend/.env файл:"
echo "   - Установите SECRET_KEY"
echo "   - Добавьте TELEGRAM_BOT_TOKEN"
echo "   - Настройте CORS_ORIGINS"
echo ""
echo "2. Настройте SSL сертификат:"
echo "   certbot --nginx -d your-domain.com"
echo ""
echo "3. Настройте домен в DNS"
echo ""
echo "4. Перезапустите сервисы после изменений:"
echo "   sudo systemctl restart pax-backend"
echo "   sudo systemctl restart nginx"
echo ""
echo "🔍 Логи сервисов:"
echo "   sudo journalctl -u pax-backend -f"
echo "   sudo tail -f /var/log/nginx/access.log"
echo ""
echo "✅ Готово к продакшену!" 