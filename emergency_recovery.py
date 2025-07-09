#!/usr/bin/env python3
"""
ЭКСТРЕННЫЙ СКРИПТ ВОССТАНОВЛЕНИЯ PAX
Версия: 1.0
Дата: 2025-07-09
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def log(message: str, level: str = "INFO"):
    """Логирование с временными метками"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def run_command(command: str, cwd: str = None) -> bool:
    """Выполнение команды с обработкой ошибок"""
    try:
        log(f"Выполняю команду: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            log(f"Команда выполнена успешно")
            if result.stdout:
                log(f"Вывод: {result.stdout.strip()}")
            return True
        else:
            log(f"Ошибка выполнения команды: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"Исключение при выполнении команды: {str(e)}", "ERROR")
        return False

def backup_current_state():
    """Создание резервной копии текущего состояния"""
    log("Создание резервной копии...")
    
    backup_dir = f"backups/emergency_backup_{os.getenv('TIMESTAMP', 'now')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Копируем критические файлы
    critical_files = [
        "backend/requirements.txt",
        "backend/app/main.py",
        "backend/app/middleware/performance.py",
        "backend/app/schemas/",
        "backend/.env"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            if os.path.isdir(file_path):
                shutil.copytree(file_path, f"{backup_dir}/{file_path}")
            else:
                shutil.copy2(file_path, f"{backup_dir}/{file_path}")
    
    log(f"Резервная копия создана в {backup_dir}")
    return backup_dir

def fix_requirements():
    """Исправление requirements.txt"""
    log("Исправление зависимостей...")
    
    requirements_file = "backend/requirements.txt"
    if not os.path.exists(requirements_file):
        log("Файл requirements.txt не найден!", "ERROR")
        return False
    
    # Читаем текущие зависимости
    with open(requirements_file, 'r') as f:
        content = f.read()
    
    # Проверяем наличие psutil
    if 'psutil' not in content:
        log("Добавляю psutil в requirements.txt...")
        content += "\npsutil==5.9.6\n"
        
        with open(requirements_file, 'w') as f:
            f.write(content)
        
        log("psutil добавлен в requirements.txt")
    
    return True

def fix_pydantic_configs():
    """Исправление конфигураций Pydantic"""
    log("Исправление конфигураций Pydantic...")
    
    schema_files = [
        "backend/app/schemas/ride.py",
        "backend/app/schemas/chat.py", 
        "backend/app/schemas/upload.py",
        "backend/app/schemas/user.py"
    ]
    
    for file_path in schema_files:
        if os.path.exists(file_path):
            log(f"Обрабатываю {file_path}...")
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Заменяем orm_mode на from_attributes
            if 'orm_mode = True' in content:
                content = content.replace('orm_mode = True', 'from_attributes = True')
                
                with open(file_path, 'w') as f:
                    f.write(content)
                
                log(f"Исправлен {file_path}")
    
    return True

def fix_middleware():
    """Исправление middleware"""
    log("Исправление middleware...")
    
    middleware_file = "backend/app/middleware/performance.py"
    if not os.path.exists(middleware_file):
        log("Файл middleware не найден!", "ERROR")
        return False
    
    # Создаем альтернативную версию без psutil
    alternative_content = '''import time
import os
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ..utils.logger import performance_logger, get_logger

logger = get_logger("performance_middleware")

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware для мониторинга производительности API"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Получаем информацию о запросе
        method = request.method
        url = str(request.url)
        user_id = None
        
        # Пытаемся получить user_id из заголовков или параметров
        try:
            # Проверяем заголовки авторизации
            auth_header = request.headers.get("authorization")
            if auth_header:
                # Здесь можно добавить логику извлечения user_id из токена
                pass
            
            # Проверяем параметры запроса
            if "user_id" in request.query_params:
                user_id = request.query_params.get("user_id")
        except Exception as e:
            logger.debug(f"Не удалось получить user_id: {str(e)}")
        
        # Выполняем запрос
        try:
            response = await call_next(request)
            
            # Рассчитываем время выполнения
            duration_ms = (time.time() - start_time) * 1000
            
            # Логируем производительность
            performance_logger.api_request(
                endpoint=url,
                method=method,
                duration_ms=duration_ms,
                status_code=response.status_code,
                user_id=user_id
            )
            
            # Добавляем заголовки с метриками
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
            response.headers["X-Request-ID"] = str(int(start_time * 1000))
            
            return response
            
        except Exception as e:
            # Рассчитываем время до ошибки
            duration_ms = (time.time() - start_time) * 1000
            
            # Логируем ошибку
            performance_logger.api_request(
                endpoint=url,
                method=method,
                duration_ms=duration_ms,
                status_code=500,
                user_id=user_id
            )
            
            logger.error(f"Ошибка в middleware производительности: {str(e)}")
            raise

class MemoryMonitor:
    """Монитор использования памяти (без psutil)"""
    
    @staticmethod
    def get_memory_usage() -> float:
        """Получить текущее использование памяти в МБ"""
        try:
            # Альтернативный способ получения информации о памяти
            with open('/proc/self/status', 'r') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        memory_kb = int(line.split()[1])
                        return memory_kb / 1024  # Конвертируем в МБ
            return 0.0
        except Exception as e:
            logger.error(f"Ошибка получения информации о памяти: {str(e)}")
            return 0.0
    
    @staticmethod
    def log_memory_usage(component: str):
        """Логировать использование памяти для компонента"""
        try:
            memory_mb = MemoryMonitor.get_memory_usage()
            performance_logger.memory_usage(memory_mb, component)
        except Exception as e:
            logger.error(f"Ошибка логирования использования памяти: {str(e)}")

class DatabasePerformanceMonitor:
    """Монитор производительности базы данных"""
    
    def __init__(self):
        self.query_times = {}
    
    def start_query(self, query_type: str, table: str):
        """Начать отслеживание запроса"""
        query_key = f"{query_type}_{table}_{int(time.time() * 1000)}"
        self.query_times[query_key] = {
            "type": query_type,
            "table": table,
            "start_time": time.time()
        }
        return query_key
    
    def end_query(self, query_key: str, result_count: int = 0):
        """Завершить отслеживание запроса"""
        if query_key in self.query_times:
            query_info = self.query_times[query_key]
            duration_ms = (time.time() - query_info["start_time"]) * 1000
            
            performance_logger.database_performance(
                operation=query_info["type"],
                table=query_info["table"],
                duration_ms=duration_ms,
                rows_affected=result_count
            )
            
            del self.query_times[query_key]
    
    def get_active_queries(self) -> dict:
        """Получить активные запросы"""
        return self.query_times.copy()

# Глобальный экземпляр монитора БД
db_monitor = DatabasePerformanceMonitor()
'''
    
    with open(middleware_file, 'w') as f:
        f.write(alternative_content)
    
    log("Middleware исправлен")
    return True

def test_application():
    """Тестирование приложения"""
    log("Тестирование приложения...")
    
    # Проверяем импорты
    try:
        import sys
        sys.path.append('backend')
        
        # Тестируем основные модули
        import app.main
        log("✅ Основной модуль импортируется успешно")
        
        import app.middleware.performance
        log("✅ Middleware импортируется успешно")
        
        # Тестируем схемы
        import app.schemas.ride
        import app.schemas.chat
        import app.schemas.upload
        import app.schemas.user
        log("✅ Все схемы импортируются успешно")
        
        return True
        
    except Exception as e:
        log(f"❌ Ошибка тестирования: {str(e)}", "ERROR")
        return False

def main():
    """Основная функция восстановления"""
    log("🚨 ЗАПУСК ЭКСТРЕННОГО ВОССТАНОВЛЕНИЯ PAX")
    log("=" * 50)
    
    # Устанавливаем временную метку
    os.environ['TIMESTAMP'] = str(int(time.time()))
    
    # Создаем резервную копию
    backup_dir = backup_current_state()
    
    # Выполняем исправления
    fixes = [
        ("Исправление зависимостей", fix_requirements),
        ("Исправление конфигураций Pydantic", fix_pydantic_configs),
        ("Исправление middleware", fix_middleware)
    ]
    
    success_count = 0
    for name, fix_func in fixes:
        log(f"Выполняю: {name}")
        if fix_func():
            success_count += 1
            log(f"✅ {name} - УСПЕШНО")
        else:
            log(f"❌ {name} - ОШИБКА", "ERROR")
    
    # Тестируем приложение
    if test_application():
        log("✅ Приложение восстановлено и готово к работе!")
    else:
        log("❌ Приложение требует дополнительных исправлений", "ERROR")
    
    # Итоговый отчет
    log("=" * 50)
    log(f"ИТОГИ ВОССТАНОВЛЕНИЯ:")
    log(f"✅ Исправлений выполнено: {success_count}/{len(fixes)}")
    log(f"📁 Резервная копия: {backup_dir}")
    log(f"🔧 Следующие шаги:")
    log(f"   1. Перезапустите приложение")
    log(f"   2. Проверьте логи на наличие ошибок")
    log(f"   3. Установите psutil: pip install psutil==5.9.6")
    log("=" * 50)

if __name__ == "__main__":
    import time
    main() 