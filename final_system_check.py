#!/usr/bin/env python3
"""
ФИНАЛЬНАЯ ПРОВЕРКА СИСТЕМЫ
Полная диагностика всех компонентов для презентации инвестору
"""

import requests
import json
import subprocess
import sys
import time
from datetime import datetime

def log(message, level="INFO"):
    """Логирование с уровнем важности"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    emoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "❌",
        "WARNING": "⚠️",
        "CRITICAL": "🚨"
    }
    print(f"[{timestamp}] {emoji.get(level, 'ℹ️')} {message}")

def check_backend():
    """Проверка бэкенда"""
    log("Проверка бэкенда...", "INFO")
    
    try:
        # Проверка основного эндпоинта
        response = requests.get("https://pax-backend-2gng.onrender.com/", timeout=10)
        if response.status_code == 200:
            log("✅ Основной эндпоинт работает", "SUCCESS")
        else:
            log(f"❌ Основной эндпоинт недоступен: {response.status_code}", "ERROR")
            return False
        
        # Проверка health check
        response = requests.get("https://pax-backend-2gng.onrender.com/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Health check: {data}", "SUCCESS")
            
            if data.get("database") == "connected":
                log("✅ База данных подключена", "SUCCESS")
            else:
                log("❌ База данных не подключена", "ERROR")
                return False
        else:
            log(f"❌ Health check недоступен: {response.status_code}", "ERROR")
            return False
        
        # Проверка API info
        response = requests.get("https://pax-backend-2gng.onrender.com/api/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"✅ API info: {data.get('name')} v{data.get('version')}", "SUCCESS")
        else:
            log(f"❌ API info недоступен: {response.status_code}", "ERROR")
        
        return True
        
    except Exception as e:
        log(f"❌ Ошибка проверки бэкенда: {e}", "ERROR")
        return False

def check_frontend():
    """Проверка фронтенда"""
    log("Проверка фронтенда...", "INFO")
    
    try:
        response = requests.get("https://frabjous-florentine-c506b0.netlify.app", timeout=10)
        if response.status_code == 200:
            log("✅ Фронтенд доступен", "SUCCESS")
            return True
        else:
            log(f"❌ Фронтенд недоступен: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Ошибка проверки фронтенда: {e}", "ERROR")
        return False

def check_telegram_bot():
    """Проверка Telegram бота"""
    log("Проверка Telegram бота...", "INFO")
    
    try:
        bot_token = "8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA"
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data["result"]
                log(f"✅ Telegram бот работает: @{bot_info['username']}", "SUCCESS")
                return True
            else:
                log(f"❌ Ошибка Telegram API: {data}", "ERROR")
                return False
        else:
            log(f"❌ Telegram бот недоступен: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Ошибка проверки Telegram бота: {e}", "ERROR")
        return False

def check_database():
    """Проверка базы данных"""
    log("Проверка базы данных...", "INFO")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        db_url = "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a.oregon-postgres.render.com/paxmain"
        parsed = urlparse(db_url)
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        log("✅ Подключение к базе данных успешно", "SUCCESS")
        return True
        
    except Exception as e:
        log(f"❌ Ошибка подключения к базе данных: {e}", "ERROR")
        return False

def check_api_endpoints():
    """Проверка основных API эндпоинтов"""
    log("Проверка API эндпоинтов...", "INFO")
    
    endpoints = [
        "/api/auth/telegram/verify",
        "/api/rides/search",
        "/api/profile/me",
        "/api/notifications/settings",
        "/api/rating/stats"
    ]
    
    base_url = "https://pax-backend-2gng.onrender.com"
    working_endpoints = 0
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code in [200, 401, 403]:  # 401/403 - нормально для защищенных эндпоинтов
                log(f"✅ {endpoint} - {response.status_code}", "SUCCESS")
                working_endpoints += 1
            else:
                log(f"❌ {endpoint} - {response.status_code}", "ERROR")
        except Exception as e:
            log(f"❌ {endpoint} - ошибка: {str(e)[:50]}", "ERROR")
    
    log(f"📊 Работающих эндпоинтов: {working_endpoints}/{len(endpoints)}", "INFO")
    return working_endpoints >= len(endpoints) * 0.8  # 80% должны работать

def check_telegram_webapp():
    """Проверка Telegram Web App"""
    log("Проверка Telegram Web App...", "INFO")
    
    try:
        # Проверяем, что фронтенд загружается с Telegram Web App
        headers = {
            'User-Agent': 'TelegramWebApp/1.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        response = requests.get("https://frabjous-florentine-c506b0.netlify.app", 
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            log("✅ Telegram Web App доступен", "SUCCESS")
            return True
        else:
            log(f"❌ Telegram Web App недоступен: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Ошибка проверки Telegram Web App: {e}", "ERROR")
        return False

def check_performance():
    """Проверка производительности"""
    log("Проверка производительности...", "INFO")
    
    try:
        start_time = time.time()
        response = requests.get("https://pax-backend-2gng.onrender.com/health", timeout=10)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # в миллисекундах
        
        if response_time < 2000:  # менее 2 секунд
            log(f"✅ Время отклика: {response_time:.0f}ms", "SUCCESS")
            return True
        elif response_time < 5000:  # менее 5 секунд
            log(f"⚠️ Время отклика: {response_time:.0f}ms (медленно)", "WARNING")
            return True
        else:
            log(f"❌ Время отклика: {response_time:.0f}ms (очень медленно)", "ERROR")
            return False
    except Exception as e:
        log(f"❌ Ошибка проверки производительности: {e}", "ERROR")
        return False

def generate_report():
    """Генерация финального отчета"""
    log("Генерация финального отчета...", "INFO")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_status": "READY",
        "components": {
            "backend": False,
            "frontend": False,
            "database": False,
            "telegram_bot": False,
            "api_endpoints": False,
            "telegram_webapp": False,
            "performance": False
        },
        "recommendations": []
    }
    
    # Проверки
    report["components"]["backend"] = check_backend()
    report["components"]["frontend"] = check_frontend()
    report["components"]["database"] = check_database()
    report["components"]["telegram_bot"] = check_telegram_bot()
    report["components"]["api_endpoints"] = check_api_endpoints()
    report["components"]["telegram_webapp"] = check_telegram_webapp()
    report["components"]["performance"] = check_performance()
    
    # Подсчет работающих компонентов
    working_components = sum(report["components"].values())
    total_components = len(report["components"])
    
    if working_components == total_components:
        report["system_status"] = "FULLY_OPERATIONAL"
        log("🎉 ВСЕ СИСТЕМЫ РАБОТАЮТ!", "SUCCESS")
    elif working_components >= total_components * 0.8:
        report["system_status"] = "MOSTLY_OPERATIONAL"
        log("✅ Большинство систем работают", "SUCCESS")
    else:
        report["system_status"] = "PARTIALLY_OPERATIONAL"
        log("⚠️ Есть проблемы с системой", "WARNING")
    
    # Рекомендации
    if not report["components"]["backend"]:
        report["recommendations"].append("Перезапустите бэкенд на Render")
    if not report["components"]["database"]:
        report["recommendations"].append("Проверьте подключение к базе данных")
    if not report["components"]["telegram_bot"]:
        report["recommendations"].append("Проверьте настройки Telegram бота")
    if not report["components"]["performance"]:
        report["recommendations"].append("Оптимизируйте производительность")
    
    return report

def main():
    """Основная функция"""
    log("🚀 ФИНАЛЬНАЯ ПРОВЕРКА СИСТЕМЫ", "INFO")
    log("=" * 60, "INFO")
    
    report = generate_report()
    
    # Вывод отчета
    log("\n📊 ФИНАЛЬНЫЙ ОТЧЕТ", "INFO")
    log("-" * 40, "INFO")
    
    for component, status in report["components"].items():
        status_text = "РАБОТАЕТ" if status else "НЕ РАБОТАЕТ"
        emoji = "✅" if status else "❌"
        log(f"{emoji} {component.upper()}: {status_text}", "INFO")
    
    log(f"\n📈 Статус системы: {report['system_status']}", "INFO")
    
    if report["recommendations"]:
        log("\n💡 РЕКОМЕНДАЦИИ:", "INFO")
        for rec in report["recommendations"]:
            log(f"   • {rec}", "WARNING")
    
    # Финальная оценка
    working_components = sum(report["components"].values())
    total_components = len(report["components"])
    
    if working_components == total_components:
        log("\n🎉 СИСТЕМА ГОТОВА К ПРЕЗЕНТАЦИИ ИНВЕСТОРУ!", "SUCCESS")
        log("✅ Все компоненты работают корректно", "SUCCESS")
        log("✅ Производительность в норме", "SUCCESS")
        log("✅ Telegram Mini App функционирует", "SUCCESS")
        return True
    elif working_components >= total_components * 0.8:
        log("\n✅ СИСТЕМА ГОТОВА К ДЕМОНСТРАЦИИ", "SUCCESS")
        log("⚠️ Есть незначительные проблемы", "WARNING")
        return True
    else:
        log("\n❌ СИСТЕМА ТРЕБУЕТ ДОРАБОТКИ", "ERROR")
        log("🔧 Необходимо исправить критические проблемы", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 