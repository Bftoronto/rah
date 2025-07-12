#!/usr/bin/env node

/**
 * 🚨 ЭКСТРЕННЫЙ ТЕСТ ВОССТАНОВЛЕНИЯ СИСТЕМЫ
 * Проверка исправления критической ошибки импорта
 */

console.log('🚨 ЭКСТРЕННЫЙ ТЕСТ ВОССТАНОВЛЕНИЯ');
console.log('=================================');

const fs = require('fs');
const path = require('path');

// Функция для проверки файла
function checkFile(filePath, description) {
    console.log(`\n📁 Проверка ${description}:`);
    console.log(`   Файл: ${filePath}`);
    
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Проверка на критические ошибки
        const issues = [];
        
        // 1. Множественные default exports
        const defaultExports = content.match(/export\s+{\s*\w+\s+as\s+default\s*}/g) || [];
        if (defaultExports.length > 1) {
            issues.push(`Найдено ${defaultExports.length} default exports`);
        }
        
        // 2. Проблемный импорт default + named
        const problematicImports = content.match(/import\s+\w+\s*,\s*{\s*\w+\s*}\s+from/g) || [];
        if (problematicImports.length > 0) {
            issues.push(`Найдено ${problematicImports.length} проблемных импортов`);
        }
        
        // 3. Star exports конфликты
        const starExports = content.match(/export\s+\*\s+from/g) || [];
        const namedExports = content.match(/export\s+{\s*\w+.*}/g) || [];
        if (starExports.length > 0 && namedExports.length > 0) {
            issues.push('Потенциальный конфликт star exports и named exports');
        }
        
        if (issues.length === 0) {
            console.log('   ✅ Файл корректен');
            return true;
        } else {
            console.log('   ❌ Найдены проблемы:');
            issues.forEach(issue => console.log(`      - ${issue}`));
            return false;
        }
        
    } catch (error) {
        console.log(`   ❌ Ошибка чтения файла: ${error.message}`);
        return false;
    }
}

// Проверяем критические файлы
const criticalFiles = [
    {
        path: 'frontend/assets/js/router.js',
        description: 'Router.js (основной файл с ошибкой)'
    },
    {
        path: 'frontend/assets/js/screens/index.js',
        description: 'Screens/index.js (экспорты экранов)'
    },
    {
        path: 'frontend/assets/js/screens/registration.js',
        description: 'Registration.js (экраны регистрации)'
    },
    {
        path: 'frontend/assets/js/app.js',
        description: 'App.js (основное приложение)'
    }
];

let allPassed = true;

criticalFiles.forEach(file => {
    const passed = checkFile(file.path, file.description);
    if (!passed) {
        allPassed = false;
    }
});

// Дополнительные проверки
console.log('\n🔍 ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ:');

// Проверка синтаксиса
const jsFiles = criticalFiles.map(f => f.path);
let syntaxOK = true;

jsFiles.forEach(file => {
    try {
        const { execSync } = require('child_process');
        execSync(`node -c "${file}"`, { stdio: 'pipe' });
        console.log(`   ✅ ${file} - синтаксис корректен`);
    } catch (error) {
        console.log(`   ❌ ${file} - синтаксическая ошибка`);
        syntaxOK = false;
        allPassed = false;
    }
});

// Проверка специфических паттернов
console.log('\n🎯 СПЕЦИФИЧЕСКИЕ ПРОВЕРКИ:');

// Проверяем что router.js не импортирует screens как default
const routerContent = fs.readFileSync('frontend/assets/js/router.js', 'utf8');
const hasProblematicImport = routerContent.includes('import screens,');
if (hasProblematicImport) {
    console.log('   ❌ В router.js остался проблемный импорт');
    allPassed = false;
} else {
    console.log('   ✅ Проблемный импорт в router.js исправлен');
}

// Проверяем что screens/index.js не экспортирует screens as default
const screensContent = fs.readFileSync('frontend/assets/js/screens/index.js', 'utf8');
const hasProblematicExport = screensContent.includes('export { screens as default }');
if (hasProblematicExport) {
    console.log('   ❌ В screens/index.js остался проблемный экспорт');
    allPassed = false;
} else {
    console.log('   ✅ Проблемный экспорт в screens/index.js исправлен');
}

// Итоговый результат
console.log('\n📊 РЕЗУЛЬТАТ ЭКСТРЕННОГО ТЕСТА:');
console.log('================================');

if (allPassed) {
    console.log('✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ');
    console.log('🎉 КРИТИЧЕСКАЯ ОШИБКА УСТРАНЕНА');
    console.log('');
    console.log('🚀 ПЛАН ДАЛЬНЕЙШИХ ДЕЙСТВИЙ:');
    console.log('1. Немедленно deploy на Netlify');
    console.log('2. Проверить логи backend на отсутствие ошибок');
    console.log('3. Тестировать в браузере');
    console.log('4. Мониторить в течение 30 минут');
    console.log('');
    console.log('📈 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:');
    console.log('- Полное устранение ошибки импорта');
    console.log('- Стабильная работа приложения');
    console.log('- Отсутствие повторяющихся ошибок в логах');
} else {
    console.log('❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ');
    console.log('🔧 ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНОЕ ИСПРАВЛЕНИЕ');
    console.log('');
    console.log('⚠️  КРИТИЧЕСКОЕ ВНИМАНИЕ:');
    console.log('Система все еще может работать нестабильно');
}

console.log('\n⏰ Время выполнения теста:', new Date().toLocaleTimeString());
console.log('💡 Создано экстренной системой диагностики');
