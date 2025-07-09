#!/bin/bash

# Скрипт мониторинга и обслуживания сервера
# Использование: ./server_maintenance.sh <server_ip> [ssh_key_path]

set -e

if [ $# -eq 0 ]; then
    echo "❌ Ошибка: Укажите IP адрес сервера"
    echo "Использование: ./server_maintenance.sh <server_ip> [ssh_key_path]"
    echo "Пример: ./server_maintenance.sh 192.168.1.100 ~/.ssh/id_rsa"
    exit 1
fi

SERVER_IP=$1
SSH_KEY=${2:-"~/.ssh/id_rsa"}
SSH_USER="root"

echo "🔧 Мониторинг и обслуживание сервера PAX"
echo "=========================================="

# Проверка подключения к серверу
echo "🔍 Проверка подключения к серверу..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$SSH_USER@$SERVER_IP" exit 2>/dev/null; then
    echo "❌ Не удалось подключиться к серверу"
    exit 1
fi

echo "✅ Подключение к серверу успешно"

# Выполнение команд мониторинга
ssh -i "$SSH_KEY" "$SSH_USER@$SERVER_IP" << 'EOF'
set -e

echo "📊 СТАТУС СИСТЕМЫ"
echo "=================="

echo "🖥️  Информация о системе:"
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo "Uptime: $(uptime -p)"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}')"

echo ""
echo "💾 Использование диска:"
df -h / | tail -1

echo ""
echo "🧠 Использование памяти:"
free -h

echo ""
echo "🌐 Сетевые соединения:"
ss -tuln | grep -E ':(80|443|8000|5432|6379)' || echo "Нет активных соединений"

echo ""
echo "📊 СТАТУС СЕРВИСОВ"
echo "=================="

echo "🔧 Pax Backend:"
systemctl is-active pax-backend && echo "✅ Активен" || echo "❌ Неактивен"

echo "🌐 Nginx:"
systemctl is-active nginx && echo "✅ Активен" || echo "❌ Неактивен"

echo "🗄️  PostgreSQL:"
systemctl is-active postgresql && echo "✅ Активен" || echo "❌ Неактивен"

echo "🔴 Redis:"
systemctl is-active redis-server && echo "✅ Активен" || echo "❌ Неактивен"

echo ""
echo "📈 ПРОИЗВОДИТЕЛЬНОСТЬ"
echo "====================="

echo "🔧 Backend метрики:"
curl -s http://localhost:8000/metrics 2>/dev/null | grep -E "(requests_total|response_time)" || echo "Метрики недоступны"

echo ""
echo "🗄️  База данных:"
sudo -u postgres psql -d pax_db -c "SELECT COUNT(*) as users FROM users;" 2>/dev/null || echo "БД недоступна"
sudo -u postgres psql -d pax_db -c "SELECT COUNT(*) as rides FROM rides;" 2>/dev/null || echo "БД недоступна"

echo ""
echo "📋 ПОСЛЕДНИЕ ЛОГИ"
echo "================="

echo "🔧 Backend логи (последние 10 строк):"
journalctl -u pax-backend --no-pager -n 10

echo ""
echo "🌐 Nginx логи (последние 10 строк):"
tail -n 10 /var/log/nginx/access.log 2>/dev/null || echo "Логи недоступны"

echo ""
echo "🔧 ОБСЛУЖИВАНИЕ"
echo "==============="

echo "🧹 Очистка старых логов..."
journalctl --vacuum-time=7d

echo "🗄️  Очистка старых файлов..."
find /opt/pax-app/uploads -type f -mtime +30 -delete 2>/dev/null || echo "Нет файлов для удаления"

echo "📦 Обновление системы..."
apt update > /dev/null 2>&1
UPGRADES=$(apt list --upgradable 2>/dev/null | wc -l)
echo "Доступно обновлений: $((UPGRADES - 1))"

echo ""
echo "🔍 ПРОВЕРКА БЕЗОПАСНОСТИ"
echo "========================="

echo "🔒 SSL сертификаты:"
certbot certificates 2>/dev/null | grep -E "(VALID|EXPIRY)" || echo "SSL не настроен"

echo "🌐 Открытые порты:"
ss -tuln | grep -E ':(22|80|443|8000)' || echo "Нет открытых портов"

echo ""
echo "📊 РЕКОМЕНДАЦИИ"
echo "==============="

# Проверка использования диска
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  Использование диска: ${DISK_USAGE}% - рекомендуется очистка"
fi

# Проверка использования памяти
MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ "$MEM_USAGE" -gt 80 ]; then
    echo "⚠️  Использование памяти: ${MEM_USAGE}% - рекомендуется перезагрузка"
fi

# Проверка SSL сертификатов
if command -v certbot >/dev/null 2>&1; then
    SSL_EXPIRY=$(certbot certificates 2>/dev/null | grep "VALID" | head -1 | awk '{print $2}')
    if [ -n "$SSL_EXPIRY" ]; then
        echo "✅ SSL сертификат действителен до: $SSL_EXPIRY"
    else
        echo "⚠️  SSL сертификат не настроен"
    fi
fi

echo ""
echo "✅ Мониторинг завершен!"
EOF

echo ""
echo "🎉 МОНИТОРИНГ ЗАВЕРШЕН!"
echo "========================"
echo ""
echo "📋 Полезные команды для управления:"
echo "   Перезапуск backend: sudo systemctl restart pax-backend"
echo "   Перезапуск nginx: sudo systemctl restart nginx"
echo "   Просмотр логов: sudo journalctl -u pax-backend -f"
echo "   Обновление системы: sudo apt update && sudo apt upgrade -y"
echo ""
echo "✅ Готово!" 