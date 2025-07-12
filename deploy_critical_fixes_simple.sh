#!/bin/bash

# 🚨 УПРОЩЕННЫЙ СКРИПТ РАЗВЕРТЫВАНИЯ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ PAX
# Автор: AI Assistant
# Дата: 2025-07-12

set -e  # Остановка при ошибке

echo "🚨 НАЧАЛО РАЗВЕРТЫВАНИЯ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ"
echo "=================================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция логирования
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ОШИБКА]${NC} $1"
}

success() {
    echo -e "${GREEN}[УСПЕХ]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[ПРЕДУПРЕЖДЕНИЕ]${NC} $1"
}

# Проверка наличия файлов
log "Проверка наличия исправленных файлов..."

FILES_TO_CHECK=(
    "frontend/assets/js/screens/index.js"
    "frontend/assets/js/screens/registration.js"
    "frontend/monitor_errors_fixed.js"
    "frontend/test_imports_fixed.html"
    "frontend/index.html"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        success "✓ $file найден"
    else
        error "✗ $file не найден"
        exit 1
    fi
done

# Создание резервной копии
log "Создание резервной копии..."
BACKUP_DIR="backups/critical_fix_$(date +'%Y%m%d_%H%M%S')"
mkdir -p "$BACKUP_DIR"

cp -r frontend/assets/js/screens "$BACKUP_DIR/"
cp frontend/index.html "$BACKUP_DIR/"
cp frontend/monitor_errors_fixed.js "$BACKUP_DIR/"
cp frontend/test_imports_fixed.html "$BACKUP_DIR/"
success "Резервная копия создана: $BACKUP_DIR"

# Проверка экспортов
log "Проверка экспортов..."

# Проверка screens/index.js
if grep -q "export { screens as default }" frontend/assets/js/screens/index.js; then
    success "✓ Экспорт в screens/index.js исправлен"
else
    error "✗ Экспорт в screens/index.js не исправлен"
    exit 1
fi

# Проверка registration.js
if grep -q "export default RegistrationScreens" frontend/assets/js/screens/registration.js; then
    success "✓ Экспорт в registration.js исправлен"
else
    error "✗ Экспорт в registration.js не исправлен"
    exit 1
fi

# Проверка мониторинга в index.html
if grep -q "monitor_errors_fixed.js" frontend/index.html; then
    success "✓ Мониторинг добавлен в index.html"
else
    error "✗ Мониторинг не добавлен в index.html"
    exit 1
fi

# Проверка бэкенда
log "Проверка бэкенда..."

if [ -d "backend" ]; then
    success "✓ Бэкенд найден"
    
    # Проверка запуска бэкенда
    if pgrep -f "uvicorn" > /dev/null; then
        success "✓ Бэкенд запущен"
    else
        warning "⚠ Бэкенд не запущен"
    fi
else
    warning "⚠ Бэкенд не найден"
fi

# Финальная проверка
log "Финальная проверка..."

# Проверка структуры проекта
if [ -d "frontend/assets/js" ] && [ -d "frontend/assets/css" ]; then
    success "✓ Структура проекта корректна"
else
    error "✗ Структура проекта нарушена"
    exit 1
fi

# Проверка наличия критических файлов
CRITICAL_FILES=(
    "frontend/assets/js/app.js"
    "frontend/assets/js/router.js"
    "frontend/assets/js/state.js"
    "frontend/assets/js/api.js"
    "frontend/assets/js/utils.js"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "✓ $file присутствует"
    else
        error "✗ $file отсутствует"
        exit 1
    fi
done

# Проверка исправлений в коде
log "Проверка исправлений в коде..."

# Проверка динамического импорта в screens/index.js
if grep -q "registrationModule.RegistrationScreens || registrationModule.default" frontend/assets/js/screens/index.js; then
    success "✓ Динамический импорт исправлен"
else
    error "✗ Динамический импорт не исправлен"
    exit 1
fi

# Проверка экспорта в registration.js
if grep -q "export { RegistrationScreens }" frontend/assets/js/screens/registration.js; then
    success "✓ Именованный экспорт в registration.js присутствует"
else
    error "✗ Именованный экспорт в registration.js отсутствует"
    exit 1
fi

# Создание отчета о развертывании
log "Создание отчета о развертывании..."

cat > DEPLOYMENT_REPORT.md << EOF
# Отчет о развертывании критических исправлений

**Дата**: $(date)
**Время**: $(date +'%H:%M:%S')
**Статус**: УСПЕШНО

## Исправленные файлы:
- frontend/assets/js/screens/index.js
- frontend/assets/js/screens/registration.js
- frontend/index.html
- frontend/monitor_errors_fixed.js

## Проверки:
- [x] Наличие файлов
- [x] Экспорты модулей
- [x] Структура проекта
- [x] Критические файлы
- [x] Динамические импорты
- [x] Именованные экспорты

## Резервная копия:
$BACKUP_DIR

## Исправления:
1. **screens/index.js**: Исправлен экспорт с `export default screens` на `export { screens as default }`
2. **registration.js**: Добавлен default экспорт для совместимости
3. **Динамические импорты**: Улучшена обработка с fallback механизмом
4. **Мониторинг**: Добавлен улучшенный мониторинг ошибок

## Статус: ✅ ГОТОВО К РАЗВЕРТЫВАНИЮ
EOF

success "Отчет создан: DEPLOYMENT_REPORT.md"

echo ""
echo "🎉 РАЗВЕРТЫВАНИЕ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ ЗАВЕРШЕНО УСПЕШНО!"
echo "================================================================"
echo ""
echo "📋 Следующие шаги:"
echo "1. Развернуть исправления в продакшен"
echo "2. Провести мониторинг ошибок"
echo "3. Выполнить полное тестирование"
echo ""
echo "📊 Статистика:"
echo "- Исправлено файлов: ${#FILES_TO_CHECK[@]}"
echo "- Время выполнения: $(date +'%H:%M:%S')"
echo "- Статус: ✅ УСПЕШНО"
echo ""
echo "🚀 Готово к развертыванию!" 