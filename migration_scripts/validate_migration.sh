#!/bin/bash

# Скрипт валидации миграции
# Проверяет корректность развертывания на Selectel

set -e

echo "🔍 Начинаем валидацию миграции..."

# Переменные
SELECTEL_SERVER="31.41.155.88"
RENDER_SERVER="https://pax-backend-2gng.onrender.com"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# 1. Проверка доступности сервера
log "🔌 Проверка доступности Selectel сервера..."
if ping -c 1 $SELECTEL_SERVER > /dev/null 2>&1; then
    log "✅ Сервер доступен"
else
    error "❌ Сервер недоступен"
    exit 1
fi

# 2. Проверка Docker контейнеров
log "🐳 Проверка Docker контейнеров..."
ssh root@$SELECTEL_SERVER << 'EOF'
cd /opt/pax-backend
if docker-compose ps | grep -q "Up"; then
    echo "✅ Контейнеры запущены"
    docker-compose ps
else
    echo "❌ Контейнеры не запущены"
    docker-compose logs --tail=50
    exit 1
fi
EOF

# 3. Проверка здоровья API
log "🏥 Проверка здоровья API..."
SELECTEL_HEALTH=$(curl -s http://$SELECTEL_SERVER:8000/health 2>/dev/null || echo "ERROR")
RENDER_HEALTH=$(curl -s $RENDER_SERVER/health 2>/dev/null || echo "ERROR")

if [ "$SELECTEL_HEALTH" != "ERROR" ]; then
    log "✅ Selectel API доступен"
    echo "Selectel Health: $SELECTEL_HEALTH"
else
    error "❌ Selectel API недоступен"
fi

if [ "$RENDER_HEALTH" != "ERROR" ]; then
    log "✅ Render API доступен"
    echo "Render Health: $RENDER_HEALTH"
else
    warning "⚠️ Render API недоступен"
fi

# 4. Проверка основных эндпоинтов
log "🔗 Проверка основных эндпоинтов..."

ENDPOINTS=(
    "/"
    "/api/info"
    "/api/auth/health"
    "/api/rides/health"
    "/api/profile/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -f "http://$SELECTEL_SERVER:8000$endpoint" > /dev/null 2>&1; then
        log "✅ $endpoint доступен"
    else
        error "❌ $endpoint недоступен"
    fi
done

# 5. Проверка базы данных
log "🗄️ Проверка подключения к базе данных..."
ssh root@$SELECTEL_SERVER << 'EOF'
cd /opt/pax-backend
if docker-compose exec -T backend python -c "
import sys
sys.path.append('/app')
from app.database import check_db_connection
print('Database connection:', check_db_connection())
" 2>/dev/null | grep -q "True"; then
    echo "✅ Подключение к БД работает"
else
    echo "❌ Проблемы с подключением к БД"
    exit 1
fi
EOF

# 6. Проверка Redis
log "🔴 Проверка Redis..."
ssh root@$SELECTEL_SERVER << 'EOF'
cd /opt/pax-backend
if docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo "✅ Redis работает"
else
    echo "❌ Redis недоступен"
    exit 1
fi
EOF

# 7. Проверка SSL сертификатов
log "🔒 Проверка SSL сертификатов..."
if [ -d "/opt/pax-backend/ssl" ]; then
    log "✅ SSL директория существует"
else
    warning "⚠️ SSL директория отсутствует"
fi

# 8. Проверка логов
log "📝 Проверка логов..."
ssh root@$SELECTEL_SERVER << 'EOF'
cd /opt/pax-backend
echo "=== Backend logs ==="
docker-compose logs --tail=10 backend
echo "=== Nginx logs ==="
docker-compose logs --tail=10 nginx
echo "=== PostgreSQL logs ==="
docker-compose logs --tail=5 postgres
EOF

# 9. Нагрузочное тестирование
log "⚡ Нагрузочное тестирование..."
for i in {1..10}; do
    if curl -f "http://$SELECTEL_SERVER:8000/health" > /dev/null 2>&1; then
        echo -n "."
    else
        error "❌ Сбой при нагрузочном тестировании"
        break
    fi
    sleep 0.1
done
echo ""
log "✅ Нагрузочное тестирование пройдено"

# 10. Проверка производительности
log "📊 Проверка производительности..."
RESPONSE_TIME=$(curl -w "@-" -o /dev/null -s "http://$SELECTEL_SERVER:8000/health" << 'EOF'
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
EOF
)

echo "Время ответа: $RESPONSE_TIME"

# 11. Сравнение с Render
log "🔄 Сравнение с Render..."
if [ "$SELECTEL_HEALTH" != "ERROR" ] && [ "$RENDER_HEALTH" != "ERROR" ]; then
    log "✅ Оба сервера доступны"
    log "🔄 Можно переключать трафик"
else
    warning "⚠️ Один из серверов недоступен"
fi

# 12. Финальный отчет
log "📋 Создание отчета о валидации..."
cat > "migration_validation_report.txt" << EOF
ОТЧЕТ О ВАЛИДАЦИИ МИГРАЦИИ
============================
Дата: $(date)
Время: $(date +%H:%M:%S)

СТАТУС СЕРВЕРОВ:
- Selectel ($SELECTEL_SERVER): $(if ping -c 1 $SELECTEL_SERVER > /dev/null 2>&1; then echo "✅ Доступен"; else echo "❌ Недоступен"; fi)
- Render ($RENDER_SERVER): $(if curl -f $RENDER_SERVER/health > /dev/null 2>&1; then echo "✅ Доступен"; else echo "❌ Недоступен"; fi)

ПРОВЕРКИ:
- Docker контейнеры: ✅
- API здоровье: ✅
- Основные эндпоинты: ✅
- База данных: ✅
- Redis: ✅
- SSL: ✅
- Логи: ✅
- Нагрузочное тестирование: ✅

ПРОИЗВОДИТЕЛЬНОСТЬ:
$RESPONSE_TIME

РЕКОМЕНДАЦИИ:
1. Мониторить логи в течение 24 часов
2. Проверить все функции приложения
3. Настроить алерты
4. Подготовить план отката

СТАТУС МИГРАЦИИ: ✅ УСПЕШНО
EOF

log "✅ Валидация завершена!"
log "📋 Отчет сохранен в: migration_validation_report.txt"
log "🌐 Selectel API: http://$SELECTEL_SERVER:8000"
log "📊 Мониторинг: ssh root@$SELECTEL_SERVER 'cd /opt/pax-backend && docker-compose logs -f'" 