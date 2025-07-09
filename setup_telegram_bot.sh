#!/bin/bash

# Скрипт настройки Telegram бота
# Использование: ./setup_telegram_bot.sh <server_ip> <bot_token> <domain> [ssh_key_path]

set -e

if [ $# -lt 3 ]; then
    echo "❌ Ошибка: Укажите IP сервера, токен бота и домен"
    echo "Использование: ./setup_telegram_bot.sh <server_ip> <bot_token> <domain> [ssh_key_path]"
    echo "Пример: ./setup_telegram_bot.sh 192.168.1.100 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz myapp.com ~/.ssh/id_rsa"
    exit 1
fi

SERVER_IP=$1
BOT_TOKEN=$2
DOMAIN=$3
SSH_KEY=${4:-"~/.ssh/id_rsa"}
SSH_USER="root"

echo "🤖 Настройка Telegram бота"
echo "=========================="
echo "Сервер: $SERVER_IP"
echo "Домен: $DOMAIN"
echo "Токен бота: ${BOT_TOKEN:0:10}..."

# Проверка подключения к серверу
echo "🔍 Проверка подключения к серверу..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$SSH_USER@$SERVER_IP" exit 2>/dev/null; then
    echo "❌ Не удалось подключиться к серверу"
    exit 1
fi

echo "✅ Подключение к серверу успешно"

# Настройка Telegram бота
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << EOF
set -e

echo "🔧 Обновление .env файла с токеном бота..."
sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$BOT_TOKEN|" /opt/pax-app/backend/.env

echo "🔧 Настройка webhook URL..."
WEBHOOK_URL="https://$DOMAIN/api/auth/telegram/webhook"

echo "📡 Установка webhook для бота..."
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \\
     -H "Content-Type: application/json" \\
     -d "{\\"url\\": \\"$WEBHOOK_URL\\"}"

echo "📊 Проверка webhook статуса..."
curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" | jq '.'

echo "🔧 Перезапуск backend сервиса..."
systemctl restart pax-backend

echo "⏳ Ожидание запуска сервиса..."
sleep 5

echo "🔍 Проверка доступности webhook..."
curl -f "https://$DOMAIN/api/auth/telegram/verify" || echo "⚠️  Webhook может быть недоступен"

echo "✅ Telegram бот настроен успешно!"
EOF

echo ""
echo "🎉 TELEGRAM БОТ НАСТРОЕН!"
echo "========================="
echo ""
echo "🤖 Bot Token: ${BOT_TOKEN:0:10}..."
echo "🌐 Webhook URL: https://$DOMAIN/api/auth/telegram/webhook"
echo ""
echo "📋 Следующие шаги:"
echo "1. Протестируйте бота, отправив команду /start"
echo "2. Проверьте логи бота:"
echo "   sudo journalctl -u pax-backend -f"
echo ""
echo "🔍 Полезные команды для проверки:"
echo "   curl -s 'https://api.telegram.org/bot$BOT_TOKEN/getMe'"
echo "   curl -s 'https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo'"
echo ""
echo "✅ Готово к использованию!" 