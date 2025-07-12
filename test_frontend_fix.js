#!/usr/bin/env node

/**
 * Экстренный тест исправлений фронтенда
 * Проверяет исправление ошибки ES6 модулей
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 ТЕСТИРОВАНИЕ ИСПРАВЛЕНИЙ ФРОНТЕНДА');
console.log('=====================================\n');

// Проверяем исправленные файлы
const filesToCheck = [
    'frontend/assets/js/screens/index.js',
    'frontend/assets/js/router.js',
    'frontend/assets/js/app.js'
];

let allTestsPassed = true;

filesToCheck.forEach(filePath => {
    console.log(`📁 Проверка файла: ${filePath}`);
    
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Проверяем наличие критических ошибок
        const hasMultipleExports = (content.match(/export default/g) || []).length > 1;
        const hasRegistrationImport = content.includes('import { RegistrationScreens }');
        const hasDynamicImport = content.includes('await import(');
        const hasAsyncInit = content.includes('async init()');
        
        if (hasMultipleExports) {
            console.log('❌ ОШИБКА: Обнаружены множественные export default');
            allTestsPassed = false;
        } else {
            console.log('✅ Нет множественных export default');
        }
        
        if (hasRegistrationImport) {
            console.log('❌ ОШИБКА: Обнаружен статический импорт RegistrationScreens');
            allTestsPassed = false;
        } else {
            console.log('✅ Нет статических импортов RegistrationScreens');
        }
        
        if (hasDynamicImport) {
            console.log('✅ Обнаружен динамический импорт');
        } else {
            console.log('⚠️  Не найден динамический импорт');
        }
        
        if (hasAsyncInit) {
            console.log('✅ Обнаружена асинхронная инициализация');
        } else {
            console.log('⚠️  Не найдена асинхронная инициализация');
        }
        
    } catch (error) {
        console.log(`❌ ОШИБКА: Не удалось прочитать файл ${filePath}: ${error.message}`);
        allTestsPassed = false;
    }
    
    console.log('');
});

// Проверяем синтаксис JavaScript
console.log('🔍 Проверка синтаксиса JavaScript...');

try {
    const { execSync } = require('child_process');
    
    // Проверяем основные файлы на синтаксические ошибки
    const jsFiles = [
        'frontend/assets/js/screens/index.js',
        'frontend/assets/js/router.js',
        'frontend/assets/js/app.js'
    ];
    
    jsFiles.forEach(file => {
        try {
            // Простая проверка синтаксиса через node
            execSync(`node -c "${file}"`, { stdio: 'pipe' });
            console.log(`✅ ${file} - синтаксис корректен`);
        } catch (error) {
            console.log(`❌ ${file} - синтаксическая ошибка: ${error.message}`);
            allTestsPassed = false;
        }
    });
    
} catch (error) {
    console.log('⚠️  Не удалось проверить синтаксис JavaScript');
}

console.log('\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:');
console.log('============================');

if (allTestsPassed) {
    console.log('✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ');
    console.log('🎉 Исправления применены успешно');
    console.log('\n🚀 РЕКОМЕНДАЦИИ:');
    console.log('1. Перезапустите фронтенд на Netlify');
    console.log('2. Проверьте работу в браузере');
    console.log('3. Мониторьте логи на предмет новых ошибок');
} else {
    console.log('❌ ОБНАРУЖЕНЫ ОШИБКИ');
    console.log('🔧 Требуется дополнительное исправление');
}

console.log('\n📝 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ:');
console.log('- Устранение ошибки "Importing binding name default cannot be resolved"');
console.log('- Корректная загрузка экранов регистрации');
console.log('- Стабильная работа приложения');

console.log('\n⏰ Время выполнения теста:', new Date().toLocaleTimeString()); 