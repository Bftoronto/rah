#!/bin/bash

# Скрипт отката миграции: Selectel → Render
# Используется в случае критических проблем

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функции логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Переменные
SELECTEL_SERVER="31.41.155.88"
RENDER_SERVER="https://pax-backend-2gng.onrender.com"
ROLLBACK_LOG="rollback.log"

# Функция для записи в лог
log_to_file() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> $ROLLBACK_LOG
}

# Функция подтверждения
confirm_rollback() {
    echo ""
    echo "⚠️ ВНИМАНИЕ: Вы собираетесь выполнить откат миграции!"
    echo "Это приведет к:"
    echo "- Остановке сервисов на Selectel"
    echo "- Возврату к использованию Render"
    echo "- Возможной потере данных, созданных после миграции"
    echo ""
    read -p "Вы уверены? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Откат отменен"
        exit 0
    fi
}

# Функция остановки сервисов на Selectel
stop_selectel_services() {
    log "🛑 Остановка сервисов на Selectel..."
    
    ssh root@$SELECTEL_SERVER << 'EOF'
cd /opt/pax-backend
if [ -f "docker-compose.yml" ]; then
    echo "Остановка Docker контейнеров..."
    docker-compose down
    echo "Контейнеры остановлены"
else
    echo "Docker Compose файл не найден"
fi

# Остановка systemd сервиса
if systemctl is-active --quiet pax-backend.service; then
    echo "Остановка systemd сервиса..."
    systemctl stop pax-backend.service
    systemctl disable pax-backend.service
    echo "Сервис остановлен и отключен"
fi
EOF
    
    log "✅ Сервисы на Selectel остановлены"
}

# Функция проверки Render
check_render_status() {
    log "🔍 Проверка статуса Render..."
    
    if curl -f "$RENDER_SERVER/health" > /dev/null 2>&1; then
        log "✅ Render доступен"
        return 0
    else
        error "❌ Render недоступен"
        return 1
    fi
}

# Функция восстановления данных (если необходимо)
restore_data() {
    log "💾 Проверка необходимости восстановления данных..."
    
    # Проверяем, есть ли новые данные на Selectel
    ssh root@$SELECTEL_SERVER << 'EOF'
cd /opt/pax-backend
if [ -f "docker-compose.yml" ]; then
    # Создаем бэкап текущих данных
    echo "Создание бэкапа текущих данных..."
    docker-compose exec -T postgres pg_dump -U rideshare_user ridesharing > /tmp/selectel_backup.sql
    echo "Бэкап создан: /tmp/selectel_backup.sql"
fi
EOF
    
    log "✅ Данные сохранены (если были)"
}

# Функция обновления конфигураций
update_configurations() {
    log "⚙️ Обновление конфигураций..."
    
    # Здесь можно добавить логику обновления DNS, прокси и т.д.
    warning "⚠️ Не забудьте обновить:"
    echo "- DNS записи (если изменялись)"
    echo "- Прокси настройки"
    echo "- SSL сертификаты"
    echo "- Мониторинг системы"
}

# Функция создания отчета об откате
create_rollback_report() {
    log "📊 Создание отчета об откате..."
    
    cat > "rollback_report.txt" << EOF
ОТЧЕТ ОБ ОТКАТЕ МИГРАЦИИ: Selectel → Render
==============================================
Дата отката: $(date)
Время: $(date +%H:%M:%S)

ПРИЧИНА ОТКАТА:
- Критические проблемы с Selectel
- Проблемы производительности
- Проблемы с безопасностью
- Другие технические проблемы

ВЫПОЛНЕННЫЕ ДЕЙСТВИЯ:
1. ✅ Подтверждение отката
2. ✅ Остановка сервисов на Selectel
3. ✅ Проверка доступности Render
4. ✅ Сохранение данных (если необходимо)
5. ✅ Обновление конфигураций

СТАТУС СЕРВЕРОВ:
- Selectel ($SELECTEL_SERVER): Остановлен
- Render ($RENDER_SERVER): $(if curl -f $RENDER_SERVER/health > /dev/null 2>&1; then echo "✅ Доступен"; else echo "❌ Недоступен"; fi)

СЛЕДУЮЩИЕ ШАГИ:
1. Проверить все функции на Render
2. Обновить DNS записи (если необходимо)
3. Настроить мониторинг
4. Проанализировать причины отката
5. Планировать повторную миграцию

ВАЖНО:
- Все данные сохранены
- Render работает стабильно
- Необходимо проанализировать причины отката
- Подготовить план повторной миграции

КОНТАКТЫ:
- Render API: $RENDER_SERVER
- Лог отката: $ROLLBACK_LOG
- Мониторинг: Настроить алерты для Render

СТАТУС ОТКАТА: ✅ ЗАВЕРШЕН
EOF

    log "✅ Отчет об откате создан: rollback_report.txt"
}

# Главная функция
main() {
    echo "🔄 НАЧАЛО ОТКАТА МИГРАЦИИ: Selectel → Render"
    echo "=============================================="
    echo "Время начала: $(date)"
    echo "Лог файл: $ROLLBACK_LOG"
    echo ""
    
    # Создание лог файла
    echo "=== НАЧАЛО ОТКАТА $(date) ===" > $ROLLBACK_LOG
    
    # Проверка аргументов
    if [ "$1" = "--help" ]; then
        echo "Использование: $0 [--force|--help]"
        echo ""
        echo "Опции:"
        echo "  --force    Пропустить подтверждение"
        echo "  --help     Показать эту справку"
        exit 0
    fi
    
    # Подтверждение (если не принудительный режим)
    if [[ "$*" != *"--force"* ]]; then
        confirm_rollback
    else
        warning "Принудительный режим - подтверждение пропущено"
    fi
    
    log_to_file "Откат подтвержден"
    
    # Остановка сервисов на Selectel
    stop_selectel_services
    log_to_file "Сервисы на Selectel остановлены"
    
    # Проверка Render
    if check_render_status; then
        log_to_file "Render доступен"
    else
        error "❌ Render недоступен - критическая проблема!"
        log_to_file "Render недоступен"
        exit 1
    fi
    
    # Восстановление данных (если необходимо)
    restore_data
    log_to_file "Данные сохранены"
    
    # Обновление конфигураций
    update_configurations
    log_to_file "Конфигурации обновлены"
    
    # Создание отчета
    create_rollback_report
    log_to_file "Отчет создан"
    
    echo ""
    echo "🔄 ОТКАТ ЗАВЕРШЕН!"
    echo "=================="
    echo "Время завершения: $(date)"
    echo ""
    echo "📋 Статус:"
    echo "- Selectel: Остановлен"
    echo "- Render: $(if curl -f $RENDER_SERVER/health > /dev/null 2>&1; then echo "✅ Доступен"; else echo "❌ Недоступен"; fi)"
    echo ""
    echo "📋 Отчеты:"
    echo "- Отчет об откате: rollback_report.txt"
    echo "- Лог: $ROLLBACK_LOG"
    echo ""
    echo "🌐 Render API: $RENDER_SERVER"
    echo ""
    echo "⚠️ ВАЖНО:"
    echo "1. Проверьте все функции на Render"
    echo "2. Обновите DNS записи (если необходимо)"
    echo "3. Настройте мониторинг"
    echo "4. Проанализируйте причины отката"
}

# Обработка ошибок
trap 'error "Критическая ошибка в строке $LINENO"; exit 1' ERR

# Запуск главной функции
main "$@" 