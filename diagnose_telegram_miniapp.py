#!/usr/bin/env python3
"""
Диагностический скрипт для проверки проблем с Telegram Mini App
"""

import requests
import json
import time
from datetime import datetime

def check_server_status():
    """Проверка статуса серверов"""
    print("🔍 Проверка статуса серверов...")
    
    servers = {
        "Backend (Render)": "https://pax-backend-2gng.onrender.com",
        "Frontend (Netlify)": "https://frabjous-florentine-c506b0.netlify.app"
    }
    
    for name, url in servers.items():
        try:
            response = requests.get(url, timeout=10)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"{status} {name}: {response.status_code} - {url}")
        except Exception as e:
            print(f"❌ {name}: Ошибка - {e}")

def check_cors_configuration():
    """Проверка CORS конфигурации"""
    print("\n🔍 Проверка CORS конфигурации...")
    
    backend_url = "https://pax-backend-2gng.onrender.com"
    origins = [
        "https://web.telegram.org",
        "https://t.me",
        "https://frabjous-florentine-c506b0.netlify.app"
    ]
    
    for origin in origins:
        try:
            headers = {
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            response = requests.options(
                f"{backend_url}/api/auth/telegram/verify",
                headers=headers,
                timeout=10
            )
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
            }
            
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"{status} {origin}: {response.status_code}")
            
            for header, value in cors_headers.items():
                if value:
                    print(f"   {header}: {value}")
                    
        except Exception as e:
            print(f"❌ {origin}: Ошибка - {e}")

def check_telegram_api_endpoints():
    """Проверка Telegram API эндпоинтов"""
    print("\n🔍 Проверка Telegram API эндпоинтов...")
    
    backend_url = "https://pax-backend-2gng.onrender.com"
    endpoints = [
        "/api/auth/telegram/verify",
        "/api/auth/telegram/webhook",
        "/api/rides/search",
        "/api/user/profile"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{backend_url}{endpoint}", timeout=10)
            status = "✅" if response.status_code in [200, 405] else "⚠️"
            print(f"{status} {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Ошибка - {e}")

def check_free_tier_limitations():
    """Проверка ограничений бесплатных тарифов"""
    print("\n🔍 Анализ ограничений бесплатных тарифов...")
    
    limitations = {
        "Render (Backend)": [
            "Спин-даун после 15 минут неактивности",
            "Ограниченная пропускная способность",
            "Возможные задержки при холодном старте",
            "Ограничения на количество запросов"
        ],
        "Netlify (Frontend)": [
            "Ограничения на количество деплоев",
            "Возможные задержки при первом запросе",
            "Ограничения на размер файлов"
        ]
    }
    
    for service, limits in limitations.items():
        print(f"\n📋 {service}:")
        for limit in limits:
            print(f"   ⚠️ {limit}")

def check_telegram_webapp_requirements():
    """Проверка требований Telegram Web App"""
    print("\n🔍 Проверка требований Telegram Web App...")
    
    requirements = [
        "HTTPS протокол (обязательно)",
        "Валидный SSL сертификат",
        "Правильная CORS конфигурация",
        "Доступность сервера 24/7",
        "Быстрый ответ сервера (< 3 сек)",
        "Поддержка Web App API"
    ]
    
    for req in requirements:
        print(f"   ✅ {req}")

def generate_recommendations():
    """Генерация рекомендаций"""
    print("\n💡 Рекомендации для решения проблем:")
    
    recommendations = [
        "1. Переход на платные тарифы Selectel:",
        "   - Устранение спин-даунов",
        "   - Стабильная производительность",
        "   - Выделенные ресурсы",
        "   - Техническая поддержка",
        "",
        "2. Оптимизация для бесплатных тарифов:",
        "   - Добавить keep-alive механизмы",
        "   - Реализовать кэширование",
        "   - Оптимизировать размер бандла",
        "   - Использовать CDN для статических файлов",
        "",
        "3. Мониторинг и диагностика:",
        "   - Добавить логирование ошибок",
        "   - Реализовать health checks",
        "   - Настроить алерты при недоступности",
        "",
        "4. Альтернативные решения:",
        "   - Использование Vercel для фронтенда",
        "   - Heroku для бэкенда",
        "   - DigitalOcean App Platform"
    ]
    
    for rec in recommendations:
        print(rec)

def main():
    """Основная функция диагностики"""
    print("🔧 Диагностика Telegram Mini App")
    print("=" * 50)
    print(f"Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_server_status()
    check_cors_configuration()
    check_telegram_api_endpoints()
    check_free_tier_limitations()
    check_telegram_webapp_requirements()
    generate_recommendations()
    
    print("\n" + "=" * 50)
    print("✅ Диагностика завершена")

if __name__ == "__main__":
    main() 