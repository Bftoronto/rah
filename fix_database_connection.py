#!/usr/bin/env python3
"""
ДИАГНОСТИКА И ИСПРАВЛЕНИЕ ПРОБЛЕМ С БАЗОЙ ДАННЫХ
"""

import requests
import json
import subprocess
import sys
from datetime import datetime

def log(message):
    """Логирование с временной меткой"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_backend_database_status():
    """Проверка статуса базы данных через бэкенд"""
    try:
        url = "https://pax-backend-2gng.onrender.com/health"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            log(f"✅ Бэкенд отвечает: {data}")
            
            if data.get("database") == "connected":
                log("✅ База данных подключена (по данным бэкенда)")
                return True
            else:
                log("❌ База данных не подключена (по данным бэкенда)")
                return False
        else:
            log(f"❌ Бэкенд недоступен: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ Ошибка проверки бэкенда: {e}")
        return False

def check_database_url():
    """Проверка корректности URL базы данных"""
    db_url = "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain"
    
    log(f"📋 URL базы данных: {db_url}")
    
    # Парсинг URL
    parts = db_url.split('@')
    if len(parts) != 2:
        log("❌ Неверный формат URL базы данных")
        return False
    
    auth_part = parts[0].replace('postgresql://', '')
    host_part = parts[1]
    
    username = auth_part.split(':')[0]
    password = auth_part.split(':')[1]
    
    host_port = host_part.split('/')[0]
    database = host_part.split('/')[1]
    
    host = host_port.split(':')[0] if ':' in host_port else host_port
    port = host_port.split(':')[1] if ':' in host_port else '5432'
    
    log(f"📋 Параметры подключения:")
    log(f"   - Хост: {host}")
    log(f"   - Порт: {port}")
    log(f"   - База данных: {database}")
    log(f"   - Пользователь: {username}")
    log(f"   - Пароль: {'*' * len(password)}")
    
    return True

def check_network_connectivity():
    """Проверка сетевого подключения к хосту базы данных"""
    host = "dpg-d1lu8jnfte5s73dv6780-a"
    
    try:
        log(f"🔍 Проверка подключения к {host}...")
        
        # Проверка DNS
        result = subprocess.run(['nslookup', host], capture_output=True, text=True)
        if result.returncode == 0:
            log("✅ DNS разрешение успешно")
        else:
            log("❌ Проблема с DNS разрешением")
            return False
        
        # Проверка ping (если доступен)
        try:
            result = subprocess.run(['ping', '-c', '3', host], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                log("✅ Ping успешен")
            else:
                log("⚠️ Ping не прошел (может быть заблокирован)")
        except subprocess.TimeoutExpired:
            log("⚠️ Ping превысил таймаут")
        except FileNotFoundError:
            log("⚠️ Команда ping недоступна")
        
        return True
        
    except Exception as e:
        log(f"❌ Ошибка проверки сетевого подключения: {e}")
        return False

def check_alternative_database_urls():
    """Проверка альтернативных URL базы данных"""
    alternative_urls = [
        "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a.oregon-postgres.render.com/paxmain",
        "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a.oregon-postgres.render.com:5432/paxmain",
        "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain?sslmode=require"
    ]
    
    log("🔍 Проверка альтернативных URL базы данных...")
    
    for i, url in enumerate(alternative_urls, 1):
        log(f"📋 Вариант {i}: {url}")
        
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            parsed = urlparse(url)
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                connect_timeout=5
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            log(f"✅ Вариант {i} работает!")
            return url
            
        except Exception as e:
            log(f"❌ Вариант {i} не работает: {str(e)[:100]}...")
    
    return None

def check_render_database_status():
    """Проверка статуса базы данных на Render"""
    try:
        # Попытка получить информацию о базе данных через Render API
        log("🔍 Проверка статуса базы данных на Render...")
        
        # Проверяем доступность через стандартные порты
        ports = [5432, 5433, 5434]
        host = "dpg-d1lu8jnfte5s73dv6780-a"
        
        for port in ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    log(f"✅ Порт {port} открыт на {host}")
                else:
                    log(f"❌ Порт {port} закрыт на {host}")
                    
            except Exception as e:
                log(f"❌ Ошибка проверки порта {port}: {e}")
        
        return True
        
    except Exception as e:
        log(f"❌ Ошибка проверки Render: {e}")
        return False

def main():
    """Основная функция диагностики"""
    log("🔍 ДИАГНОСТИКА ПРОБЛЕМ С БАЗОЙ ДАННЫХ")
    log("=" * 50)
    
    # 1. Проверка URL базы данных
    check_database_url()
    
    # 2. Проверка сетевого подключения
    check_network_connectivity()
    
    # 3. Проверка статуса через бэкенд
    backend_db_ok = check_backend_database_status()
    
    # 4. Проверка альтернативных URL
    working_url = check_alternative_database_urls()
    
    # 5. Проверка Render
    check_render_database_status()
    
    # 6. Итоговый отчет
    log("\n📊 ИТОГОВЫЙ ОТЧЕТ")
    log("-" * 30)
    
    if backend_db_ok:
        log("✅ База данных работает (по данным бэкенда)")
    else:
        log("❌ База данных не работает (по данным бэкенда)")
    
    if working_url:
        log(f"✅ Найден рабочий URL: {working_url}")
    else:
        log("❌ Рабочий URL не найден")
    
    # 7. Рекомендации
    log("\n💡 РЕКОМЕНДАЦИИ")
    log("-" * 30)
    
    if not backend_db_ok:
        log("🔧 Перезапустите бэкенд на Render")
        log("   - Зайдите в Render Dashboard")
        log("   - Найдите сервис pax-backend-2gng")
        log("   - Нажмите 'Manual Deploy'")
    
    if working_url:
        log("🔧 Обновите URL базы данных в конфигурации")
        log(f"   - Новый URL: {working_url}")
        log("   - Обновите переменные окружения")
    
    if not working_url and not backend_db_ok:
        log("🔧 Проверьте статус базы данных на Render")
        log("   - Зайдите в Render Dashboard")
        log("   - Найдите базу данных paxmain")
        log("   - Убедитесь, что она активна")
    
    # 8. Успешное завершение
    if backend_db_ok:
        log("\n🎉 БАЗА ДАННЫХ РАБОТАЕТ!")
        return True
    else:
        log("\n⚠️ ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 