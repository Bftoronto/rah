#!/bin/bash

# Скрипт быстрого запуска проекта PAX

echo "🚀 Запуск проекта PAX - Система поиска попутчиков"
echo "================================================="

# Проверка Python
echo "📋 Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+"
    exit 1
fi

# Проверка Docker
echo "📋 Проверка Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не найден. Установите Docker"
    exit 1
fi

# Проверка Docker Compose
echo "📋 Проверка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не найден. Установите Docker Compose"
    exit 1
fi

echo "✅ Все зависимости найдены"

# Переход в папку backend
cd backend

# Создание .env файла если его нет
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cp .env.example .env
    echo "⚠️  ВАЖНО: Отредактируйте backend/.env файл с вашими настройками!"
    echo "   Особенно TELEGRAM_BOT_TOKEN и SECRET_KEY"
fi

echo "🐳 Запуск Docker контейнеров..."

# Остановка существующих контейнеров
docker-compose down

# Сборка и запуск
docker-compose up --build -d

echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка статуса контейнеров
echo "📊 Статус контейнеров:"
docker-compose ps

# Применение миграций
echo "🔧 Применение миграций базы данных..."
docker-compose exec backend alembic upgrade head

echo ""
echo "🎉 ПРОЕКТ ЗАПУЩЕН!"
echo "=================="
echo ""
echo "📱 Frontend: http://localhost (или http://localhost:80)"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API документация: http://localhost:8000/docs"
echo "📊 Health Check: http://localhost:8000/health"
echo ""
echo "🔍 Логи backend: docker-compose logs -f backend"
echo "🔍 Логи nginx: docker-compose logs -f nginx"
echo "🔍 Логи PostgreSQL: docker-compose logs -f postgres"
echo ""
echo "🛑 Остановка: docker-compose down"
echo ""
echo "📋 Следующие шаги:"
echo "1. Настройте Telegram бота (см. BOT_SETUP.md)"
echo "2. Добавьте SSL сертификат для продакшена"
echo "3. Настройте домен"
echo ""
echo "✅ Готово к демонстрации инвестору!"
