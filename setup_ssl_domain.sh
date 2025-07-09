#!/bin/bash

# Скрипт настройки SSL сертификата и домена
# Использование: ./setup_ssl_domain.sh <server_ip> <domain> [ssh_key_path]

set -e

if [ $# -lt 2 ]; then
    echo "❌ Ошибка: Укажите IP сервера и домен"
    echo "Использование: ./setup_ssl_domain.sh <server_ip> <domain> [ssh_key_path]"
    echo "Пример: ./setup_ssl_domain.sh 192.168.1.100 myapp.com ~/.ssh/id_rsa"
    exit 1
fi

SERVER_IP=$1
DOMAIN=$2
SSH_KEY=${3:-"~/.ssh/id_rsa"}
SSH_USER="root"

echo "🔒 Настройка SSL сертификата для домена $DOMAIN"
echo "================================================"

# Проверка подключения к серверу
echo "🔍 Проверка подключения к серверу..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$SSH_USER@$SERVER_IP" exit 2>/dev/null; then
    echo "❌ Не удалось подключиться к серверу"
    exit 1
fi

echo "✅ Подключение к серверу успешно"

# Настройка домена и SSL
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << EOF
set -e

echo "🔧 Обновление конфигурации Nginx для домена $DOMAIN..."

# Создание новой конфигурации Nginx с доменом
cat > /etc/nginx/sites-available/pax-app << 'NGINX'
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Frontend
    location / {
        root /opt/pax-app;
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

echo "🔧 Перезапуск Nginx..."
systemctl restart nginx

echo "🔒 Получение SSL сертификата..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

echo "🔧 Обновление .env файла с новым доменом..."
sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,https://web.telegram.org|" /opt/pax-app/backend/.env

echo "🔧 Перезапуск backend сервиса..."
systemctl restart pax-backend

echo "📊 Проверка SSL сертификата..."
curl -I https://$DOMAIN

echo "🔧 Настройка автоматического обновления SSL..."
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -

echo "✅ SSL сертификат настроен успешно!"
EOF

echo ""
echo "🎉 SSL СЕРТИФИКАТ НАСТРОЕН!"
echo "============================"
echo ""
echo "🌐 Домен: https://$DOMAIN"
echo "📱 Frontend: https://$DOMAIN"
echo "🔧 Backend API: https://$DOMAIN/api"
echo "📚 API документация: https://$DOMAIN/api/docs"
echo ""
echo "⚠️  ВАЖНЫЕ СЛЕДУЮЩИЕ ШАГИ:"
echo "1. Убедитесь, что DNS записи настроены правильно:"
echo "   A $DOMAIN -> $SERVER_IP"
echo "   A www.$DOMAIN -> $SERVER_IP"
echo ""
echo "2. Настройте Telegram Webhook URL:"
echo "   https://$DOMAIN/api/auth/telegram/webhook"
echo ""
echo "3. Обновите CORS настройки в .env файле"
echo ""
echo "🔍 Проверка SSL:"
echo "   curl -I https://$DOMAIN"
echo ""
echo "✅ Готово к продакшену!" 