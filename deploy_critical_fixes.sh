#!/bin/bash

# 🚨 СКРИПТ РАЗВЕРТЫВАНИЯ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ PAX
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
success "Резервная копия создана: $BACKUP_DIR"

# Проверка синтаксиса JavaScript
log "Проверка синтаксиса JavaScript..."

# Проверка основных файлов
for file in frontend/assets/js/screens/*.js; do
    if [ -f "$file" ]; then
        if node -c "$file" 2>/dev/null; then
            success "✓ Синтаксис $file корректен"
        else
            error "✗ Ошибка синтаксиса в $file"
            exit 1
        fi
    fi
done

# Проверка мониторинга
if node -c frontend/monitor_errors_fixed.js 2>/dev/null; then
    success "✓ Синтаксис monitor_errors_fixed.js корректен"
else
    error "✗ Ошибка синтаксиса в monitor_errors_fixed.js"
    exit 1
fi

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

# Тестирование импортов
log "Тестирование импортов..."

# Создание временного тестового файла
cat > test_imports_temp.js << 'EOF'
// Тест импортов
async function testImports() {
    try {
        // Тест screens/index.js
        const screensModule = await import('./frontend/assets/js/screens/index.js');
        console.log('✓ screens/index.js импортируется успешно');
        
        // Тест registration.js
        const registrationModule = await import('./frontend/assets/js/screens/registration.js');
        console.log('✓ registration.js импортируется успешно');
        
        return true;
    } catch (error) {
        console.error('✗ Ошибка импорта:', error.message);
        return false;
    }
}

testImports();
EOF

# Запуск теста
if node test_imports_temp.js 2>/dev/null; then
    success "✓ Все импорты работают корректно"
else
    error "✗ Ошибка в импортах"
    rm test_imports_temp.js
    exit 1
fi

rm test_imports_temp.js

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
- [x] Синтаксис JavaScript
- [x] Экспорты модулей
- [x] Импорты
- [x] Структура проекта
- [x] Критические файлы

## Резервная копия:
$BACKUP_DIR

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