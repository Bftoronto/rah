#!/bin/bash

# Скрипт для запуска локального бэкенда

echo "🚀 Запуск локального бэкенда..."

# Переходим в папку backend
cd backend

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Устанавливаем зависимости
echo "📚 Установка зависимостей..."
pip install -r requirements.txt

# Устанавливаем переменные окружения
export ENVIRONMENT=development
export DEBUG=true
export TELEGRAM_BOT_TOKEN=8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA

# Запускаем сервер
echo "🌐 Запуск сервера на http://localhost:8000..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 