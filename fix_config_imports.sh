#!/bin/bash

# Скрипт исправления проблем с импортами конфигурации
# Использование: ./fix_config_imports.sh <server_ip> [ssh_key_path]

set -e

if [ $# -eq 0 ]; then
    echo "❌ Ошибка: Укажите IP адрес сервера"
    echo "Использование: ./fix_config_imports.sh <server_ip> [ssh_key_path]"
    echo "Пример: ./fix_config_imports.sh 192.168.1.100 ~/.ssh/id_rsa"
    exit 1
fi

SERVER_IP=$1
SSH_KEY=${2:-"~/.ssh/id_rsa"}
SSH_USER="root"

echo "🔧 Исправление проблем с импортами конфигурации"
echo "================================================"

# Проверка подключения к серверу
echo "🔍 Проверка подключения к серверу..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$SSH_USER@$SERVER_IP" exit 2>/dev/null; then
    echo "❌ Не удалось подключиться к серверу"
    exit 1
fi

echo "✅ Подключение к серверу успешно"

# Исправление проблемы
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << 'EOF'
set -e

echo "🔧 Переход в директорию приложения..."
cd /opt/pax-app/backend

echo "🔧 Исправление импортов в файлах..."

# Исправление database.py
if [ -f "app/database.py" ]; then
    sed -i 's/from \.config_simple import settings/from .config.settings import settings/' app/database.py
    echo "✅ Исправлен импорт в app/database.py"
fi

# Исправление notification_service.py
if [ -f "app/services/notification_service.py" ]; then
    sed -i 's/from \.\.config_simple import settings/from ..config.settings import settings/' app/services/notification_service.py
    echo "✅ Исправлен импорт в app/services/notification_service.py"
fi

# Исправление moderation_service.py
if [ -f "app/services/moderation_service.py" ]; then
    sed -i 's/from \.\.config_simple import settings/from ..config.settings import settings/' app/services/moderation_service.py
    echo "✅ Исправлен импорт в app/services/moderation_service.py"
fi

# Проверка других файлов с проблемными импортами
echo "🔍 Поиск других файлов с проблемными импортами..."
find app -name "*.py" -exec grep -l "config_simple" {} \; 2>/dev/null || echo "✅ Других проблемных файлов не найдено"

echo "🔧 Перезапуск backend сервиса..."
systemctl restart pax-backend

echo "⏳ Ожидание запуска сервиса..."
sleep 10

echo "🔍 Проверка статуса сервиса..."
systemctl status pax-backend --no-pager

echo "🔍 Проверка доступности API..."
curl -f http://localhost:8000/health && echo "✅ API доступен" || echo "❌ API недоступен"

echo "✅ Проблемы с импортами исправлены!"
EOF

echo ""
echo "🎉 ПРОБЛЕМЫ ИСПРАВЛЕНЫ!"
echo "========================"
echo ""
echo "📋 Что было исправлено:"
echo "  - Исправлены импорты config_simple на config.settings"
echo "  - Обновлены файлы: database.py, notification_service.py, moderation_service.py"
echo "  - Перезапущен backend сервис"
echo ""
echo "🔍 Проверка:"
echo "  curl http://$SERVER_IP/health"
echo ""
echo "✅ Готово!" 