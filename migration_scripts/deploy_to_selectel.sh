#!/bin/bash

# Скрипт миграции на Selectel
# Использование: ./deploy_to_selectel.sh <server_ip> <domain> [ssh_key_path]

set -e

if [ $# -lt 2 ]; then
    echo "❌ Ошибка: Укажите IP сервера и домен"
    echo "Использование: ./deploy_to_selectel.sh <server_ip> <domain> [ssh_key_path]"
    echo "Пример: ./deploy_to_selectel.sh 192.168.1.100 myapp.com ~/.ssh/id_rsa"
    exit 1
fi

SERVER_IP=$1
DOMAIN=$2
SSH_KEY=${3:-"~/.ssh/id_rsa"}
SSH_USER="root"

echo "🚀 Миграция на Selectel"
echo "========================"
echo "Сервер: $SERVER_IP"
echo "Домен: $DOMAIN"
echo "SSH ключ: $SSH_KEY"

# Проверка подключения к серверу
echo "🔍 Проверка подключения к серверу..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$SSH_USER@$SERVER_IP" exit 2>/dev/null; then
    echo "❌ Не удалось подключиться к серверу"
    exit 1
fi

echo "✅ Подключение к серверу успешно"

# Подготовка сервера
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << 'EOF'
set -e

echo "🔧 Обновление системы..."
apt update && apt upgrade -y

echo "🔧 Установка необходимых пакетов..."
apt install -y nginx postgresql postgresql-contrib redis-server python3 python3-pip python3-venv git curl certbot python3-certbot-nginx

echo "🔧 Настройка PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE paxapp;"
sudo -u postgres psql -c "CREATE USER paxuser WITH PASSWORD 'paxpassword123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE paxapp TO paxuser;"

echo "🔧 Настройка Redis..."
systemctl enable redis-server
systemctl start redis-server

echo "🔧 Создание пользователя для приложения..."
useradd -m -s /bin/bash paxapp
usermod -aG sudo paxapp

echo "🔧 Создание директорий..."
mkdir -p /opt/pax-app
mkdir -p /opt/pax-app/backend
mkdir -p /opt/pax-app/frontend
mkdir -p /opt/pax-app/logs
mkdir -p /opt/pax-app/uploads

echo "🔧 Настройка прав доступа..."
chown -R paxapp:paxapp /opt/pax-app
chmod -R 755 /opt/pax-app
EOF

# Копирование файлов приложения
echo "📁 Копирование файлов приложения..."

# Копирование backend
scp -i "$SSH_KEY" -r backend/* "$SSH_USER@$SERVER_IP:/opt/pax-app/backend/"

# Копирование frontend
scp -i "$SSH_KEY" index.html "$SSH_USER@$SERVER_IP:/opt/pax-app/frontend/"
scp -i "$SSH_KEY" -r assets "$SSH_USER@$SERVER_IP:/opt/pax-app/frontend/"

# Копирование конфигурационных файлов
scp -i "$SSH_KEY" nginx.conf "$SSH_USER@$SERVER_IP:/opt/pax-app/"
scp -i "$SSH_KEY" docker-compose.yml "$SSH_USER@$SERVER_IP:/opt/pax-app/"

# Настройка приложения на сервере
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << EOF
set -e

echo "🔧 Настройка Python окружения..."
cd /opt/pax-app/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Создание .env файла..."
cat > /opt/pax-app/backend/.env << 'ENVEOF'
DATABASE_URL=postgresql://paxuser:paxpassword123@localhost/paxapp
TELEGRAM_BOT_TOKEN=8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA
TELEGRAM_BOT_USERNAME=paxdemobot
SECRET_KEY=$(openssl rand -hex 32)
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,https://web.telegram.org
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379
ENVEOF

echo "🔧 Настройка systemd сервиса..."
cat > /etc/systemd/system/pax-backend.service << 'SERVICEEOF'
[Unit]
Description=PAX Backend Service
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=paxapp
Group=paxapp
WorkingDirectory=/opt/pax-app/backend
Environment=PATH=/opt/pax-app/backend/venv/bin
ExecStart=/opt/pax-app/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo "🔧 Настройка Nginx..."
cat > /etc/nginx/sites-available/pax-app << 'NGINXEOF'
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Frontend
    location / {
        root /opt/pax-app/frontend;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Кэширование статических файлов
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
    
    # Безопасность
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
NGINXEOF

echo "🔧 Активация Nginx конфигурации..."
ln -sf /etc/nginx/sites-available/pax-app /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t

echo "🔧 Запуск сервисов..."
systemctl daemon-reload
systemctl enable pax-backend
systemctl start pax-backend
systemctl restart nginx

echo "🔒 Получение SSL сертификата..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

echo "🔧 Финальная настройка..."
systemctl restart pax-backend
systemctl restart nginx

echo "📊 Проверка статуса сервисов..."
systemctl status pax-backend --no-pager
systemctl status nginx --no-pager
systemctl status postgresql --no-pager
systemctl status redis-server --no-pager
EOF

echo "✅ Миграция завершена успешно!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Обновите DNS записи для домена $DOMAIN"
echo "2. Настройте Telegram бота с новым URL: https://$DOMAIN"
echo "3. Протестируйте приложение: https://$DOMAIN"
echo "4. Настройте мониторинг и логирование"
echo ""
echo "🔗 Полезные команды:"
echo "  - Проверка логов: ssh $SSH_USER@$SERVER_IP 'journalctl -u pax-backend -f'"
echo "  - Перезапуск сервиса: ssh $SSH_USER@$SERVER_IP 'systemctl restart pax-backend'"
echo "  - Проверка статуса: ssh $SSH_USER@$SERVER_IP 'systemctl status pax-backend'" 