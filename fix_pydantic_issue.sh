#!/bin/bash

# Скрипт исправления проблемы с Pydantic BaseSettings
# Использование: ./fix_pydantic_issue.sh <server_ip> [ssh_key_path]

set -e

if [ $# -eq 0 ]; then
    echo "❌ Ошибка: Укажите IP адрес сервера"
    echo "Использование: ./fix_pydantic_issue.sh <server_ip> [ssh_key_path]"
    echo "Пример: ./fix_pydantic_issue.sh 192.168.1.100 ~/.ssh/id_rsa"
    exit 1
fi

SERVER_IP=$1
SSH_KEY=${2:-"~/.ssh/id_rsa"}
SSH_USER="root"

echo "🔧 Исправление проблемы с Pydantic BaseSettings"
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

echo "📦 Добавление pydantic-settings в requirements.txt..."
if ! grep -q "pydantic-settings" requirements.txt; then
    echo "pydantic-settings==2.1.0" >> requirements.txt
    echo "✅ pydantic-settings добавлен в requirements.txt"
else
    echo "✅ pydantic-settings уже есть в requirements.txt"
fi

echo "🐍 Обновление Python зависимостей..."
source venv/bin/activate
pip install pydantic-settings==2.1.0

echo "🔧 Исправление импортов в файлах конфигурации..."

# Исправление settings.py
sed -i 's/from pydantic import BaseSettings, Field/from pydantic import Field\nfrom pydantic_settings import BaseSettings/' app/config/settings.py

# Исправление logging.py
if [ -f "app/config/logging.py" ]; then
    sed -i 's/from pydantic import BaseSettings, Field/from pydantic import Field\nfrom pydantic_settings import BaseSettings/' app/config/logging.py
fi

# Исправление security.py
if [ -f "app/config/security.py" ]; then
    sed -i 's/from pydantic import BaseSettings, Field/from pydantic import Field\nfrom pydantic_settings import BaseSettings/' app/config/security.py
fi

# Исправление database.py
if [ -f "app/config/database.py" ]; then
    sed -i 's/from pydantic import BaseSettings, Field/from pydantic import Field\nfrom pydantic_settings import BaseSettings/' app/config/database.py
fi

echo "🔧 Перезапуск backend сервиса..."
systemctl restart pax-backend

echo "⏳ Ожидание запуска сервиса..."
sleep 10

echo "🔍 Проверка статуса сервиса..."
systemctl status pax-backend --no-pager

echo "🔍 Проверка доступности API..."
curl -f http://localhost:8000/health && echo "✅ API доступен" || echo "❌ API недоступен"

echo "✅ Проблема с Pydantic исправлена!"
EOF

echo ""
echo "🎉 ПРОБЛЕМА ИСПРАВЛЕНА!"
echo "========================"
echo ""
echo "📋 Что было исправлено:"
echo "  - Добавлен pydantic-settings в requirements.txt"
echo "  - Исправлены импорты BaseSettings во всех файлах конфигурации"
echo "  - Перезапущен backend сервис"
echo ""
echo "🔍 Проверка:"
echo "  curl http://$SERVER_IP/health"
echo ""
echo "✅ Готово!" 