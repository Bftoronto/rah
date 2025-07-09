#!/bin/bash

# Главный скрипт миграции: Render → Selectel
# Автоматизирует весь процесс миграции

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Переменные
SELECTEL_SERVER="31.41.155.88"
RENDER_SERVER="https://pax-backend-2gng.onrender.com"
BACKUP_DIR="./backups"
MIGRATION_LOG="migration.log"

# Функция для записи в лог
log_to_file() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> $MIGRATION_LOG
}

# Функция проверки зависимостей
check_dependencies() {
    log "🔍 Проверка зависимостей..."
    
    # Проверка необходимых команд
    commands=("curl" "ssh" "scp" "tar" "gzip" "docker")
    for cmd in "${commands[@]}"; do
        if ! command -v $cmd &> /dev/null; then
            error "❌ Команда $cmd не найдена"
            exit 1
        fi
    done
    
    # Проверка подключения к серверу
    if ! ssh -o ConnectTimeout=10 root@$SELECTEL_SERVER "echo 'Connection test'" &> /dev/null; then
        error "❌ Не удается подключиться к серверу $SELECTEL_SERVER"
        exit 1
    fi
    
    log "✅ Все зависимости проверены"
}

# Функция создания резервной копии
create_backup() {
    log "💾 Создание резервной копии с Render..."
    
    if [ ! -f "migration_scripts/backup_render_data.sh" ]; then
        error "❌ Скрипт резервного копирования не найден"
        exit 1
    fi
    
    chmod +x migration_scripts/backup_render_data.sh
    ./migration_scripts/backup_render_data.sh
    
    log "✅ Резервная копия создана"
}

# Функция подготовки сервера
prepare_server() {
    log "🔧 Подготовка сервера Selectel..."
    
    if [ ! -f "migration_scripts/prepare_selectel_server.sh" ]; then
        error "❌ Скрипт подготовки сервера не найден"
        exit 1
    fi
    
    chmod +x migration_scripts/prepare_selectel_server.sh
    scp migration_scripts/prepare_selectel_server.sh root@$SELECTEL_SERVER:/tmp/
    ssh root@$SELECTEL_SERVER "chmod +x /tmp/prepare_selectel_server.sh && /tmp/prepare_selectel_server.sh"
    
    log "✅ Сервер подготовлен"
}

# Функция развертывания
deploy_application() {
    log "🚀 Развертывание приложения на Selectel..."
    
    if [ ! -f "migration_scripts/deploy_to_selectel.sh" ]; then
        error "❌ Скрипт развертывания не найден"
        exit 1
    fi
    
    chmod +x migration_scripts/deploy_to_selectel.sh
    ./migration_scripts/deploy_to_selectel.sh
    
    log "✅ Приложение развернуто"
}

# Функция валидации
validate_migration() {
    log "🔍 Валидация миграции..."
    
    if [ ! -f "migration_scripts/validate_migration.sh" ]; then
        error "❌ Скрипт валидации не найден"
        exit 1
    fi
    
    chmod +x migration_scripts/validate_migration.sh
    ./migration_scripts/validate_migration.sh
    
    log "✅ Валидация завершена"
}

# Функция создания отчета
create_report() {
    log "📊 Создание финального отчета..."
    
    cat > "migration_final_report.txt" << EOF
ОТЧЕТ О МИГРАЦИИ: Render → Selectel
=====================================
Дата миграции: $(date)
Время начала: $(cat $MIGRATION_LOG | head -1 | cut -d' ' -f2-3)
Время завершения: $(date)

СЕРВЕРЫ:
- Источник: $RENDER_SERVER
- Назначение: $SELECTEL_SERVER

ЭТАПЫ МИГРАЦИИ:
1. ✅ Проверка зависимостей
2. ✅ Создание резервной копии
3. ✅ Подготовка сервера
4. ✅ Развертывание приложения
5. ✅ Валидация миграции

ФАЙЛЫ:
- Лог миграции: $MIGRATION_LOG
- Отчет валидации: migration_validation_report.txt
- Резервные копии: $BACKUP_DIR/

СТАТУС: ✅ УСПЕШНО

СЛЕДУЮЩИЕ ШАГИ:
1. Мониторить логи в течение 24 часов
2. Проверить все функции приложения
3. Настроить алерты и мониторинг
4. Обновить DNS записи (если необходимо)
5. Подготовить план отката

КОНТАКТЫ:
- Selectel API: http://$SELECTEL_SERVER:8000
- Мониторинг: ssh root@$SELECTEL_SERVER 'cd /opt/pax-backend && docker-compose logs -f'
- Логи: tail -f $MIGRATION_LOG

ВАЖНО:
- Сохраните все резервные копии
- Документируйте все изменения
- Подготовьте план отката
- Настройте мониторинг
EOF

    log "✅ Финальный отчет создан: migration_final_report.txt"
}

# Функция очистки
cleanup() {
    log "🧹 Очистка временных файлов..."
    
    # Очистка временных файлов на сервере
    ssh root@$SELECTEL_SERVER "rm -f /tmp/prepare_selectel_server.sh" 2>/dev/null || true
    
    log "✅ Очистка завершена"
}

# Главная функция
main() {
    echo "🚀 НАЧАЛО МИГРАЦИИ: Render → Selectel"
    echo "========================================"
    echo "Время начала: $(date)"
    echo "Лог файл: $MIGRATION_LOG"
    echo ""
    
    # Создание лог файла
    echo "=== НАЧАЛО МИГРАЦИИ $(date) ===" > $MIGRATION_LOG
    
    # Проверка аргументов
    if [ "$1" = "--help" ]; then
        echo "Использование: $0 [--skip-backup|--skip-prepare|--validate-only]"
        echo ""
        echo "Опции:"
        echo "  --skip-backup     Пропустить создание резервной копии"
        echo "  --skip-prepare    Пропустить подготовку сервера"
        echo "  --validate-only   Только валидация (без миграции)"
        echo "  --help           Показать эту справку"
        exit 0
    fi
    
    # Проверка зависимостей
    check_dependencies
    log_to_file "Зависимости проверены"
    
    # Создание резервной копии (если не пропущено)
    if [[ "$*" != *"--skip-backup"* ]]; then
        create_backup
        log_to_file "Резервная копия создана"
    else
        warning "Пропуск создания резервной копии"
        log_to_file "Создание резервной копии пропущено"
    fi
    
    # Подготовка сервера (если не пропущено)
    if [[ "$*" != *"--skip-prepare"* ]]; then
        prepare_server
        log_to_file "Сервер подготовлен"
    else
        warning "Пропуск подготовки сервера"
        log_to_file "Подготовка сервера пропущена"
    fi
    
    # Только валидация
    if [[ "$*" == *"--validate-only"* ]]; then
        warning "Режим только валидации"
        validate_migration
        exit 0
    fi
    
    # Развертывание приложения
    deploy_application
    log_to_file "Приложение развернуто"
    
    # Валидация
    validate_migration
    log_to_file "Валидация завершена"
    
    # Создание отчета
    create_report
    log_to_file "Отчет создан"
    
    # Очистка
    cleanup
    log_to_file "Очистка завершена"
    
    echo ""
    echo "🎉 МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!"
    echo "=================================="
    echo "Время завершения: $(date)"
    echo "Длительность: $(($(date +%s) - $(date -d "$(cat $MIGRATION_LOG | head -1 | cut -d' ' -f2-3)" +%s))) секунд"
    echo ""
    echo "📋 Отчеты:"
    echo "- Основной отчет: migration_final_report.txt"
    echo "- Валидация: migration_validation_report.txt"
    echo "- Лог: $MIGRATION_LOG"
    echo ""
    echo "🌐 Selectel API: http://$SELECTEL_SERVER:8000"
    echo "📊 Мониторинг: ssh root@$SELECTEL_SERVER 'cd /opt/pax-backend && docker-compose logs -f'"
    echo ""
    echo "⚠️ ВАЖНО: Проверьте все функции приложения перед переключением трафика!"
}

# Обработка ошибок
trap 'error "Критическая ошибка в строке $LINENO"; exit 1' ERR

# Запуск главной функции
main "$@" 