#!/usr/bin/env node

/**
 * 🚨 ФИНАЛЬНЫЙ ТЕСТ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ
 * Полная проверка устранения ошибки "Importing binding name 'default' cannot be resolved"
 */

console.log('🚨 ФИНАЛЬНЫЙ ТЕСТ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ');
console.log('==========================================');

const fs = require('fs');
const path = require('path');

// Список всех критических файлов для проверки
const criticalFiles = [
    {
        path: 'frontend/assets/js/router.js',
        description: 'Router - основной файл с исправлением',
        checks: [
            { type: 'not_contains', pattern: 'import screens,', message: 'Убран проблемный импорт screens' },
            { type: 'contains', pattern: 'import { getAllScreens }', message: 'Добавлен корректный импорт' }
        ]
    },
    {
        path: 'frontend/assets/js/screens/index.js',
        description: 'Screens/index.js - экспорты экранов',
        checks: [
            { type: 'not_contains', pattern: 'export { screens as default }', message: 'Убран проблемный экспорт' },
            { type: 'contains', pattern: 'export { screens }', message: 'Добавлен корректный экспорт' }
        ]
    },
    {
        path: 'frontend/test_imports.html',
        description: 'Test imports - тестовый файл',
        checks: [
            { type: 'not_contains', pattern: 'import screens from', message: 'Убран проблемный импорт в тесте' },
            { type: 'contains', pattern: 'import { screens }', message: 'Добавлен корректный импорт в тесте' }
        ]
    },
    {
        path: 'frontend/test_imports_fixed.html',
        description: 'Test imports fixed - исправленный тест',
        checks: [
            { type: 'not_contains', pattern: 'screensModule.default', message: 'Убран проблемный доступ к default' },
            { type: 'contains', pattern: 'const { screens }', message: 'Добавлен корректный импорт' }
        ]
    },
    {
        path: 'frontend/assets/js/screens/registration.js',
        description: 'Registration screens - экраны регистрации',
        checks: [
            { type: 'contains', pattern: 'export { RegistrationScreens }', message: 'Именованный экспорт присутствует' },
            { type: 'contains', pattern: 'export default RegistrationScreens', message: 'Default экспорт добавлен' }
        ]
    }
];

let allTestsPassed = true;

// Функция для проверки файла
function checkFile(fileConfig) {
    console.log(`\n📁 Проверка ${fileConfig.description}:`);
    console.log(`   Файл: ${fileConfig.path}`);
    
    try {
        const content = fs.readFileSync(fileConfig.path, 'utf8');
        let filePassed = true;
        
        fileConfig.checks.forEach(check => {
            const found = content.includes(check.pattern);
            
            if (check.type === 'contains' && found) {
                console.log(`   ✅ ${check.message}`);
            } else if (check.type === 'not_contains' && !found) {
                console.log(`   ✅ ${check.message}`);
            } else if (check.type === 'contains' && !found) {
                console.log(`   ❌ НЕ НАЙДЕНО: ${check.message}`);
                filePassed = false;
            } else if (check.type === 'not_contains' && found) {
                console.log(`   ❌ НАЙДЕНО: ${check.message}`);
                filePassed = false;
            }
        });
        
        if (filePassed) {
            console.log('   ✅ Файл полностью исправлен');
        } else {
            console.log('   ❌ Файл требует доработки');
            allTestsPassed = false;
        }
        
        return filePassed;
        
    } catch (error) {
        console.log(`   ❌ Ошибка чтения файла: ${error.message}`);
        allTestsPassed = false;
        return false;
    }
}

// Проверяем все критические файлы
console.log('\n🔍 ПРОВЕРКА КРИТИЧЕСКИХ ФАЙЛОВ:');
criticalFiles.forEach(checkFile);

// Проверка синтаксиса JavaScript
console.log('\n🔍 ПРОВЕРКА СИНТАКСИСА:');
const jsFiles = criticalFiles
    .filter(f => f.path.endsWith('.js'))
    .map(f => f.path);

jsFiles.forEach(file => {
    try {
        const { execSync } = require('child_process');
        execSync(`node -c "${file}"`, { stdio: 'pipe' });
        console.log(`   ✅ ${file} - синтаксис корректен`);
    } catch (error) {
        console.log(`   ❌ ${file} - синтаксическая ошибка`);
        allTestsPassed = false;
    }
});

// Дополнительные проверки на потенциальные проблемы
console.log('\n🎯 ДОПОЛНИТЕЛЬНЫЕ ПРОВЕРКИ:');

// Проверяем отсутствие других проблемных паттернов
const additionalPatterns = [
    'export { * as default }',
    'import * as screens from',
    'export * from.*index',
    'export { .* as default }.*from'
];

let hasAdditionalIssues = false;

criticalFiles.forEach(file => {
    try {
        const content = fs.readFileSync(file.path, 'utf8');
        
        additionalPatterns.forEach(pattern => {
            const regex = new RegExp(pattern, 'g');
            const matches = content.match(regex);
            
            if (matches) {
                console.log(`   ⚠️  ${file.path}: Найден потенциально проблемный паттерн: ${pattern}`);
                hasAdditionalIssues = true;
            }
        });
    } catch (error) {
        // Файл уже проверен выше
    }
});

if (!hasAdditionalIssues) {
    console.log('   ✅ Дополнительные проблемные паттерны не найдены');
}

// Итоговый результат
console.log('\n📊 РЕЗУЛЬТАТ ФИНАЛЬНОГО ТЕСТА:');
console.log('===============================');

if (allTestsPassed && !hasAdditionalIssues) {
    console.log('✅ ВСЕ КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ ПРИМЕНЕНЫ');
    console.log('🎉 ОШИБКА "Importing binding name \'default\' cannot be resolved" УСТРАНЕНА');
    console.log('');
    console.log('🚀 ПЛАН НЕМЕДЛЕННЫХ ДЕЙСТВИЙ:');
    console.log('1. ✅ Все файлы исправлены');
    console.log('2. 🔄 Немедленно deploy на Netlify');
    console.log('3. 📊 Проверить логи backend через 5 минут');
    console.log('4. 🌐 Тестировать в браузере');
    console.log('5. 📈 Мониторить систему в течение 30 минут');
    console.log('');
    console.log('🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:');
    console.log('- Полное исчезновение ошибки импорта из логов');
    console.log('- Стабильная работа всех экранов');
    console.log('- Корректная навигация между экранами');
    console.log('- Отсутствие JS ошибок в консоли браузера');
    console.log('');
    console.log('📱 КОМАНДА ДЛЯ РАЗВЕРТЫВАНИЯ:');
    console.log('git add .');
    console.log('git commit -m "CRITICAL FIX: Resolve star export binding issue"');
    console.log('git push origin main');
} else {
    console.log('❌ ОБНАРУЖЕНЫ НЕРЕШЕННЫЕ ПРОБЛЕМЫ');
    console.log('🔧 СИСТЕМА МОЖЕТ ОСТАВАТЬСЯ НЕСТАБИЛЬНОЙ');
    console.log('');
    console.log('⚠️  КРИТИЧЕСКОЕ ВНИМАНИЕ:');
    console.log('Требуется дополнительная диагностика и исправление');
    console.log('Не рекомендуется развертывание до полного устранения проблем');
}

console.log('\n💡 ТЕХНИЧЕСКОЕ РЕЗЮМЕ:');
console.log('Проблема заключалась в конфликте между:');
console.log('- export { screens as default } - в screens/index.js');
console.log('- import screens, { getAllScreens } - в router.js');
console.log('- star exports и named exports в одном модуле');
console.log('');
console.log('Решение:');
console.log('- Убрали default export из screens/index.js');
console.log('- Изменили импорт в router.js на named import');
console.log('- Исправили все тестовые файлы');
console.log('');
console.log('⏰ Время выполнения теста:', new Date().toLocaleTimeString());
console.log('🔧 Создано экстренной системой восстановления');
