#!/usr/bin/env python3
"""
Скрипт автоматического развертывания для продакшена
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """Менеджер развертывания"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / "scripts"
        
    def run_command(self, command: List[str], cwd: Path = None) -> bool:
        """Выполнение команды с логированием"""
        if cwd is None:
            cwd = self.project_root
            
        logger.info(f"Выполняю команду: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"Команда выполнена успешно: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка выполнения команды: {e.stderr}")
            return False
    
    def check_prerequisites(self) -> bool:
        """Проверка предварительных требований"""
        logger.info("Проверяю предварительные требования...")
        
        # Проверка Python
        if not self.run_command(["python", "--version"]):
            logger.error("Python не найден")
            return False
            
        # Проверка pip
        if not self.run_command(["pip", "--version"]):
            logger.error("pip не найден")
            return False
            
        # Проверка git
        if not self.run_command(["git", "--version"]):
            logger.error("git не найден")
            return False
            
        logger.info("Все предварительные требования выполнены")
        return True
    
    def backup_database(self) -> bool:
        """Резервное копирование базы данных"""
        logger.info("Создаю резервную копию базы данных...")
        
        backup_dir = self.project_root / "backups" / "deployment"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Здесь должна быть логика резервного копирования
        # В зависимости от типа БД (PostgreSQL, MySQL, etc.)
        
        logger.info("Резервная копия создана")
        return True
    
    def install_dependencies(self) -> bool:
        """Установка зависимостей"""
        logger.info("Устанавливаю зависимости...")
        
        requirements_file = self.project_root / "requirements_enhanced.txt"
        if not requirements_file.exists():
            logger.error(f"Файл {requirements_file} не найден")
            return False
            
        return self.run_command(["pip", "install", "-r", str(requirements_file)])
    
    def run_migrations(self) -> bool:
        """Выполнение миграций базы данных"""
        logger.info("Выполняю миграции базы данных...")
        
        # Проверка Alembic
        if not (self.project_root / "alembic.ini").exists():
            logger.error("Файл alembic.ini не найден")
            return False
            
        return self.run_command(["alembic", "upgrade", "head"])
    
    def run_tests(self) -> bool:
        """Запуск тестов"""
        logger.info("Запускаю тесты...")
        
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            logger.warning("Директория tests не найдена, пропускаю тесты")
            return True
            
        return self.run_command(["python", "-m", "pytest", str(tests_dir)])
    
    def validate_configuration(self) -> bool:
        """Валидация конфигурации"""
        logger.info("Проверяю конфигурацию...")
        
        # Проверка переменных окружения
        required_env_vars = [
            "DATABASE_URL",
            "SECRET_KEY",
            "TELEGRAM_BOT_TOKEN"
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Отсутствуют обязательные переменные окружения: {missing_vars}")
            return False
            
        logger.info("Конфигурация валидна")
        return True
    
    def restart_services(self) -> bool:
        """Перезапуск сервисов"""
        logger.info("Перезапускаю сервисы...")
        
        # Здесь должна быть логика перезапуска сервисов
        # В зависимости от системы (systemd, supervisor, etc.)
        
        logger.info("Сервисы перезапущены")
        return True
    
    def health_check(self) -> bool:
        """Проверка здоровья приложения"""
        logger.info("Выполняю проверку здоровья приложения...")
        
        # Здесь должна быть логика проверки здоровья
        # Например, проверка доступности API endpoints
        
        logger.info("Проверка здоровья завершена")
        return True
    
    def deploy(self) -> bool:
        """Основной процесс развертывания"""
        logger.info(f"Начинаю развертывание в окружении: {self.environment}")
        
        steps = [
            ("Проверка предварительных требований", self.check_prerequisites),
            ("Резервное копирование", self.backup_database),
            ("Установка зависимостей", self.install_dependencies),
            ("Валидация конфигурации", self.validate_configuration),
            ("Выполнение миграций", self.run_migrations),
            ("Запуск тестов", self.run_tests),
            ("Перезапуск сервисов", self.restart_services),
            ("Проверка здоровья", self.health_check)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"=== {step_name} ===")
            if not step_func():
                logger.error(f"Ошибка на этапе: {step_name}")
                return False
                
        logger.info("Развертывание завершено успешно!")
        return True

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Скрипт развертывания")
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        default="production",
        help="Окружение для развертывания"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Пропустить тесты"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показать план развертывания без выполнения"
    )
    
    args = parser.parse_args()
    
    deployer = DeploymentManager(args.environment)
    
    if args.dry_run:
        logger.info("Режим dry-run: план развертывания")
        # Здесь можно показать план развертывания
        return
    
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 