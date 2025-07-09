#!/usr/bin/env python3
"""
Скрипт экстренного восстановления приложения
Диагностика и исправление критических проблем
"""

import os
import sys
import logging
import subprocess
import requests
import time
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmergencyRecovery:
    """Класс для экстренного восстановления приложения"""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
        
    def check_environment_variables(self):
        """Проверка критических переменных окружения"""
        logger.info("🔍 Проверка переменных окружения...")
        
        critical_vars = [
            "DATABASE_URL",
            "TELEGRAM_BOT_TOKEN",
            "SECRET_KEY"
        ]
        
        missing_vars = []
        for var in critical_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                self.issues_found.append(f"Отсутствует переменная окружения: {var}")
        
        if missing_vars:
            logger.error(f"❌ Отсутствуют критические переменные: {missing_vars}")
            return False
        else:
            logger.info("✅ Все критические переменные окружения установлены")
            return True
    
    def check_database_connection(self):
        """Проверка подключения к базе данных"""
        logger.info("🔍 Проверка подключения к базе данных...")
        
        try:
            from app.database import check_db_connection
            if check_db_connection():
                logger.info("✅ Подключение к базе данных успешно")
                return True
            else:
                logger.error("❌ Не удалось подключиться к базе данных")
                self.issues_found.append("Ошибка подключения к базе данных")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке БД: {e}")
            self.issues_found.append(f"Ошибка проверки БД: {e}")
            return False
    
    def check_dependencies(self):
        """Проверка установленных зависимостей"""
        logger.info("🔍 Проверка зависимостей...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "psycopg2-binary",
            "pydantic"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
                self.issues_found.append(f"Отсутствует пакет: {package}")
        
        if missing_packages:
            logger.error(f"❌ Отсутствуют пакеты: {missing_packages}")
            return False
        else:
            logger.info("✅ Все необходимые пакеты установлены")
            return True
    
    def check_file_structure(self):
        """Проверка структуры файлов"""
        logger.info("🔍 Проверка структуры файлов...")
        
        required_files = [
            "app/main.py",
            "app/config_simple.py",
            "app/database.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
                self.issues_found.append(f"Отсутствует файл: {file_path}")
        
        if missing_files:
            logger.error(f"❌ Отсутствуют файлы: {missing_files}")
            return False
        else:
            logger.info("✅ Все необходимые файлы присутствуют")
            return True
    
    def fix_database_url(self):
        """Исправление URL базы данных для Render.com"""
        logger.info("🔧 Исправление URL базы данных...")
        
        database_url = os.getenv("DATABASE_URL")
        if database_url and "localhost" in database_url:
            logger.warning("⚠️ Обнаружен localhost в DATABASE_URL - это может быть проблемой в продакшене")
            self.issues_found.append("DATABASE_URL содержит localhost")
            
            # Предлагаем исправление
            if "render.com" in database_url or "postgresql://" in database_url:
                logger.info("✅ DATABASE_URL выглядит корректно для Render.com")
                return True
            else:
                logger.error("❌ DATABASE_URL не соответствует формату Render.com")
                return False
        
        return True
    
    def test_application_startup(self):
        """Тестирование запуска приложения"""
        logger.info("🔍 Тестирование запуска приложения...")
        
        try:
            # Импортируем приложение
            from app.main import app
            logger.info("✅ Приложение успешно импортировано")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка импорта приложения: {e}")
            self.issues_found.append(f"Ошибка импорта приложения: {e}")
            return False
    
    def generate_health_report(self):
        """Генерация отчета о состоянии системы"""
        logger.info("📊 Генерация отчета о состоянии...")
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "environment": os.getenv("ENVIRONMENT", "unknown"),
            "python_version": sys.version,
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied,
            "database_url": os.getenv("DATABASE_URL", "not_set")[:20] + "..." if os.getenv("DATABASE_URL") else "not_set",
            "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", "not_set")[:10] + "..." if os.getenv("TELEGRAM_BOT_TOKEN") else "not_set"
        }
        
        return report
    
    def run_full_diagnostic(self):
        """Запуск полной диагностики"""
        logger.info("🚨 ЗАПУСК ПОЛНОЙ ДИАГНОСТИКИ СИСТЕМЫ")
        logger.info("=" * 50)
        
        checks = [
            ("Проверка переменных окружения", self.check_environment_variables),
            ("Проверка структуры файлов", self.check_file_structure),
            ("Проверка зависимостей", self.check_dependencies),
            ("Исправление URL базы данных", self.fix_database_url),
            ("Тестирование импорта приложения", self.test_application_startup),
            ("Проверка подключения к БД", self.check_database_connection)
        ]
        
        results = {}
        for check_name, check_func in checks:
            logger.info(f"\n🔍 {check_name}...")
            try:
                results[check_name] = check_func()
            except Exception as e:
                logger.error(f"❌ Ошибка при выполнении {check_name}: {e}")
                results[check_name] = False
                self.issues_found.append(f"Ошибка в {check_name}: {e}")
        
        # Генерация отчета
        report = self.generate_health_report()
        report["check_results"] = results
        
        logger.info("\n" + "=" * 50)
        logger.info("📊 РЕЗУЛЬТАТЫ ДИАГНОСТИКИ")
        logger.info("=" * 50)
        
        for check_name, result in results.items():
            status = "✅ УСПЕШНО" if result else "❌ ОШИБКА"
            logger.info(f"{status}: {check_name}")
        
        if self.issues_found:
            logger.info(f"\n⚠️ НАЙДЕННЫЕ ПРОБЛЕМЫ ({len(self.issues_found)}):")
            for i, issue in enumerate(self.issues_found, 1):
                logger.info(f"{i}. {issue}")
        
        if self.fixes_applied:
            logger.info(f"\n🔧 ПРИМЕНЕННЫЕ ИСПРАВЛЕНИЯ ({len(self.fixes_applied)}):")
            for i, fix in enumerate(self.fixes_applied, 1):
                logger.info(f"{i}. {fix}")
        
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        logger.info(f"\n📈 ИТОГОВАЯ СТАТИСТИКА:")
        logger.info(f"Успешных проверок: {success_count}/{total_count}")
        logger.info(f"Найдено проблем: {len(self.issues_found)}")
        logger.info(f"Применено исправлений: {len(self.fixes_applied)}")
        
        if success_count == total_count:
            logger.info("🎉 СИСТЕМА ГОТОВА К РАБОТЕ!")
        else:
            logger.warning("⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ - ТРЕБУЕТСЯ ВМЕШАТЕЛЬСТВО")
        
        return report

def main():
    """Главная функция"""
    logger.info("🚨 ЗАПУСК СКРИПТА ЭКСТРЕННОГО ВОССТАНОВЛЕНИЯ")
    logger.info("=" * 60)
    
    recovery = EmergencyRecovery()
    report = recovery.run_full_diagnostic()
    
    # Сохранение отчета в файл
    report_file = "emergency_recovery_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("ОТЧЕТ ЭКСТРЕННОГО ВОССТАНОВЛЕНИЯ\n")
        f.write("=" * 50 + "\n")
        for key, value in report.items():
            f.write(f"{key}: {value}\n")
    
    logger.info(f"📄 Отчет сохранен в файл: {report_file}")
    
    return len(recovery.issues_found) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 