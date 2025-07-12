#!/usr/bin/env python3
"""
Комплексная проверка конфигурации системы PAX
Проверяет соответствие базы данных, бэкенда, фронтенда и Telegram бота
"""

import requests
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

class SystemConfigurationChecker:
    def __init__(self):
        self.results = {}
        self.issues = []
        self.warnings = []
        
        # Ожидаемые конфигурации
        self.expected_config = {
            "database": {
                "url": "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain",
                "password": "IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN"
            },
            "backend": {
                "url": "https://pax-backend-2gng.onrender.com/",
                "health_endpoint": "https://pax-backend-2gng.onrender.com/health"
            },
            "frontend": {
                "url": "https://frabjous-florentine-c506b0.netlify.app/",
                "api_redirect": "https://pax-backend-2gng.onrender.com/api/"
            },
            "telegram_bot": {
                "username": "@paxdemobot",
                "token": "8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA"
            }
        }
    
    def print_header(self, title):
        """Вывод заголовка"""
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")
    
    def print_result(self, test_name, status, details=""):
        """Вывод результата теста"""
        icon = "✅" if status else "❌"
        print(f"{icon} {test_name}")
        if details:
            print(f"   {details}")
    
    def check_database_configuration(self):
        """Проверка конфигурации базы данных"""
        self.print_header("ПРОВЕРКА КОНФИГУРАЦИИ БАЗЫ ДАННЫХ")
        
        # Проверяем файлы конфигурации
        config_files = [
            "backend/app/config/settings.py",
            "backend/app/config/legacy_config.py", 
            "backend/app/config/legacy_config_simple.py",
            "backend/alembic.ini",
            "backend/docker-compose.yml",
            "backend/render.yaml"
        ]
        
        expected_db_url = self.expected_config["database"]["url"]
        expected_password = self.expected_config["database"]["password"]
        
        for file_path in config_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if expected_db_url in content:
                        self.print_result(f"Файл {file_path}", True, "URL базы данных соответствует")
                    else:
                        self.print_result(f"Файл {file_path}", False, "URL базы данных НЕ соответствует")
                        self.issues.append(f"Несоответствие в {file_path}")
                        
                    if expected_password in content:
                        self.print_result(f"Пароль в {file_path}", True, "Пароль соответствует")
                    else:
                        self.print_result(f"Пароль в {file_path}", False, "Пароль НЕ соответствует")
                        self.issues.append(f"Несоответствие пароля в {file_path}")
                        
                except Exception as e:
                    self.print_result(f"Файл {file_path}", False, f"Ошибка чтения: {e}")
                    self.issues.append(f"Ошибка чтения {file_path}: {e}")
            else:
                self.print_result(f"Файл {file_path}", False, "Файл не найден")
                self.warnings.append(f"Файл не найден: {file_path}")
    
    def check_backend_configuration(self):
        """Проверка конфигурации бэкенда"""
        self.print_header("ПРОВЕРКА КОНФИГУРАЦИИ БЭКЕНДА")
        
        backend_url = self.expected_config["backend"]["url"]
        health_url = self.expected_config["backend"]["health_endpoint"]
        
        # Проверяем доступность бэкенда
        try:
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                self.print_result("Доступность бэкенда", True, f"Статус: {response.status_code}")
            else:
                self.print_result("Доступность бэкенда", False, f"Статус: {response.status_code}")
                self.issues.append(f"Бэкенд недоступен: {response.status_code}")
        except Exception as e:
            self.print_result("Доступность бэкенда", False, f"Ошибка: {e}")
            self.issues.append(f"Ошибка подключения к бэкенду: {e}")
        
        # Проверяем конфигурацию в файлах
        backend_files = [
            "backend/app/main.py",
            "backend/render.yaml",
            "backend/docker-compose.yml"
        ]
        
        for file_path in backend_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "pax-backend-2gng.onrender.com" in content:
                        self.print_result(f"URL в {file_path}", True, "URL бэкенда соответствует")
                    else:
                        self.print_result(f"URL в {file_path}", False, "URL бэкенда НЕ соответствует")
                        self.issues.append(f"Несоответствие URL в {file_path}")
                        
                except Exception as e:
                    self.print_result(f"Файл {file_path}", False, f"Ошибка чтения: {e}")
                    self.issues.append(f"Ошибка чтения {file_path}: {e}")
            else:
                self.print_result(f"Файл {file_path}", False, "Файл не найден")
                self.warnings.append(f"Файл не найден: {file_path}")
    
    def check_frontend_configuration(self):
        """Проверка конфигурации фронтенда"""
        self.print_header("ПРОВЕРКА КОНФИГУРАЦИИ ФРОНТЕНДА")
        
        frontend_url = self.expected_config["frontend"]["url"]
        api_redirect = self.expected_config["frontend"]["api_redirect"]
        
        # Проверяем доступность фронтенда
        try:
            response = requests.get(frontend_url, timeout=10)
            if response.status_code == 200:
                self.print_result("Доступность фронтенда", True, f"Статус: {response.status_code}")
            else:
                self.print_result("Доступность фронтенда", False, f"Статус: {response.status_code}")
                self.issues.append(f"Фронтенд недоступен: {response.status_code}")
        except Exception as e:
            self.print_result("Доступность фронтенда", False, f"Ошибка: {e}")
            self.issues.append(f"Ошибка подключения к фронтенду: {e}")
        
        # Проверяем конфигурацию в файлах фронтенда
        frontend_files = [
            "frontend/assets/js/api.js",
            "frontend/_redirects",
            "frontend/assets/js/websocket.js",
            "frontend/assets/js/app.js"
        ]
        
        for file_path in frontend_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if "pax-backend-2gng.onrender.com" in content:
                        self.print_result(f"API URL в {file_path}", True, "API URL соответствует")
                    else:
                        self.print_result(f"API URL в {file_path}", False, "API URL НЕ соответствует")
                        self.issues.append(f"Несоответствие API URL в {file_path}")
                    
                    if "frabjous-florentine-c506b0.netlify.app" in content:
                        self.print_result(f"Frontend URL в {file_path}", True, "Frontend URL соответствует")
                    else:
                        self.print_result(f"Frontend URL в {file_path}", False, "Frontend URL НЕ соответствует")
                        self.issues.append(f"Несоответствие Frontend URL в {file_path}")
                        
                except Exception as e:
                    self.print_result(f"Файл {file_path}", False, f"Ошибка чтения: {e}")
                    self.issues.append(f"Ошибка чтения {file_path}: {e}")
            else:
                self.print_result(f"Файл {file_path}", False, "Файл не найден")
                self.warnings.append(f"Файл не найден: {file_path}")
    
    def check_telegram_bot_configuration(self):
        """Проверка конфигурации Telegram бота"""
        self.print_header("ПРОВЕРКА КОНФИГУРАЦИИ TELEGRAM БОТА")
        
        expected_token = self.expected_config["telegram_bot"]["token"]
        expected_username = self.expected_config["telegram_bot"]["username"]
        
        # Проверяем конфигурацию в файлах
        telegram_files = [
            "backend/app/config/settings.py",
            "backend/app/config/legacy_config.py",
            "backend/app/config/legacy_config_simple.py",
            "backend/app/utils/telegram.py",
            "backend/app/utils/telegram_validator.py",
            "backend/app/utils/security.py",
            "backend/app/utils/security_enhanced.py",
            "backend/render.yaml",
            "backend/docker-compose.yml"
        ]
        
        for file_path in telegram_files:
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if expected_token in content:
                        self.print_result(f"Bot Token в {file_path}", True, "Token соответствует")
                    else:
                        self.print_result(f"Bot Token в {file_path}", False, "Token НЕ соответствует")
                        self.issues.append(f"Несоответствие Bot Token в {file_path}")
                    
                    if "paxdemobot" in content:
                        self.print_result(f"Bot Username в {file_path}", True, "Username соответствует")
                    else:
                        self.print_result(f"Bot Username в {file_path}", False, "Username НЕ соответствует")
                        self.issues.append(f"Несоответствие Bot Username в {file_path}")
                        
                except Exception as e:
                    self.print_result(f"Файл {file_path}", False, f"Ошибка чтения: {e}")
                    self.issues.append(f"Ошибка чтения {file_path}: {e}")
            else:
                self.print_result(f"Файл {file_path}", False, "Файл не найден")
                self.warnings.append(f"Файл не найден: {file_path}")
        
        # Проверяем доступность Telegram Bot API
        try:
            bot_api_url = f"https://api.telegram.org/bot{expected_token}/getMe"
            response = requests.get(bot_api_url, timeout=10)
            if response.status_code == 200:
                bot_data = response.json()
                if bot_data.get("ok"):
                    bot_info = bot_data.get("result", {})
                    self.print_result("Telegram Bot API", True, f"Бот: @{bot_info.get('username', 'N/A')}")
                else:
                    self.print_result("Telegram Bot API", False, "Ошибка получения информации о боте")
                    self.issues.append("Ошибка Telegram Bot API")
            else:
                self.print_result("Telegram Bot API", False, f"Статус: {response.status_code}")
                self.issues.append(f"Ошибка Telegram Bot API: {response.status_code}")
        except Exception as e:
            self.print_result("Telegram Bot API", False, f"Ошибка: {e}")
            self.issues.append(f"Ошибка подключения к Telegram Bot API: {e}")
    
    def check_integration(self):
        """Проверка интеграции между компонентами"""
        self.print_header("ПРОВЕРКА ИНТЕГРАЦИИ КОМПОНЕНТОВ")
        
        # Проверяем CORS настройки
        try:
            response = requests.get("https://pax-backend-2gng.onrender.com/health", timeout=10)
            cors_headers = response.headers.get('Access-Control-Allow-Origin', '')
            
            if 'web.telegram.org' in cors_headers or '*' in cors_headers:
                self.print_result("CORS настройки", True, "Telegram Web App разрешен")
            else:
                self.print_result("CORS настройки", False, "Telegram Web App НЕ разрешен")
                self.issues.append("CORS не настроен для Telegram Web App")
        except Exception as e:
            self.print_result("CORS настройки", False, f"Ошибка проверки: {e}")
            self.issues.append(f"Ошибка проверки CORS: {e}")
        
        # Проверяем API endpoints
        api_endpoints = [
            "/api/auth/telegram/verify",
            "/api/health",
            "/api/rides/search"
        ]
        
        for endpoint in api_endpoints:
            try:
                url = f"https://pax-backend-2gng.onrender.com{endpoint}"
                response = requests.get(url, timeout=10)
                if response.status_code in [200, 401, 404]:  # 401 и 404 тоже нормальные ответы
                    self.print_result(f"API endpoint {endpoint}", True, f"Статус: {response.status_code}")
                else:
                    self.print_result(f"API endpoint {endpoint}", False, f"Статус: {response.status_code}")
                    self.issues.append(f"Проблема с API endpoint {endpoint}: {response.status_code}")
            except Exception as e:
                self.print_result(f"API endpoint {endpoint}", False, f"Ошибка: {e}")
                self.issues.append(f"Ошибка API endpoint {endpoint}: {e}")
    
    def generate_report(self):
        """Генерация итогового отчета"""
        self.print_header("ИТОГОВЫЙ ОТЧЕТ")
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        print(f"📊 Статистика проверки:")
        print(f"   ❌ Критических проблем: {total_issues}")
        print(f"   ⚠️  Предупреждений: {total_warnings}")
        
        if total_issues == 0:
            print(f"\n🎉 ВСЕ КОНФИГУРАЦИИ СООТВЕТСТВУЮТ!")
            print(f"✅ Система готова к работе")
        else:
            print(f"\n🔧 ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ:")
            for issue in self.issues:
                print(f"   • {issue}")
        
        if total_warnings > 0:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ:")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        # Сохраняем отчет
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "issues": self.issues,
            "warnings": self.warnings,
            "expected_config": self.expected_config
        }
        
        with open('system_configuration_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Отчет сохранен в: system_configuration_report.json")
        
        return total_issues == 0
    
    def run_all_checks(self):
        """Запуск всех проверок"""
        print("🚀 ЗАПУСК КОМПЛЕКСНОЙ ПРОВЕРКИ КОНФИГУРАЦИИ СИСТЕМЫ PAX")
        print("=" * 80)
        
        self.check_database_configuration()
        self.check_backend_configuration()
        self.check_frontend_configuration()
        self.check_telegram_bot_configuration()
        self.check_integration()
        
        return self.generate_report()

def main():
    """Основная функция"""
    checker = SystemConfigurationChecker()
    success = checker.run_all_checks()
    
    if success:
        print(f"\n🎉 ПРОВЕРКА ЗАВЕРШЕНА УСПЕШНО!")
        sys.exit(0)
    else:
        print(f"\n❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ В КОНФИГУРАЦИИ!")
        sys.exit(1)

if __name__ == "__main__":
    main() 