#!/usr/bin/env python3
"""
Автоматическое исправление конфигурации системы PAX
Исправляет все несоответствия в файлах конфигурации
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class SystemConfigurationFixer:
    def __init__(self):
        self.fixes_applied = []
        self.errors = []
        
        # Правильные конфигурации
        self.correct_config = {
            "database_url": "postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain",
            "database_password": "IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN",
            "backend_url": "https://pax-backend-2gng.onrender.com",
            "frontend_url": "https://frabjous-florentine-c506b0.netlify.app",
            "telegram_bot_token": "8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA",
            "telegram_bot_username": "paxdemobot"
        }
    
    def print_header(self, title):
        """Вывод заголовка"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
    
    def print_result(self, action, status, details=""):
        """Вывод результата действия"""
        icon = "✅" if status else "❌"
        print(f"{icon} {action}")
        if details:
            print(f"   {details}")
    
    def backup_file(self, file_path):
        """Создание резервной копии файла"""
        try:
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            self.errors.append(f"Ошибка создания резервной копии {file_path}: {e}")
            return None
    
    def fix_database_configuration(self):
        """Исправление конфигурации базы данных"""
        self.print_header("ИСПРАВЛЕНИЕ КОНФИГУРАЦИИ БАЗЫ ДАННЫХ")
        
        files_to_fix = [
            "backend/app/config/settings.py",
            "backend/render.yaml"
        ]
        
        for file_path in files_to_fix:
            if Path(file_path).exists():
                try:
                    # Создаем резервную копию
                    backup_path = self.backup_file(file_path)
                    if not backup_path:
                        continue
                    
                    # Читаем файл
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Исправляем URL базы данных
                    old_db_url_patterns = [
                        r'DATABASE_URL.*=.*["\']([^"\']+)["\']',
                        r'database_url.*=.*["\']([^"\']+)["\']',
                        r'url.*=.*["\']([^"\']+)["\']'
                    ]
                    
                    content_fixed = content
                    for pattern in old_db_url_patterns:
                        content_fixed = re.sub(
                            pattern,
                            lambda m: m.group(0).replace(m.group(1), self.correct_config["database_url"]),
                            content_fixed
                        )
                    
                    # Исправляем пароль
                    content_fixed = content_fixed.replace(
                        "your-super-secret-jwt-key-change-in-production",
                        self.correct_config["database_password"]
                    )
                    
                    # Записываем исправленный файл
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content_fixed)
                    
                    self.print_result(f"Исправлен файл {file_path}", True, f"Резервная копия: {backup_path}")
                    self.fixes_applied.append(f"Исправлен {file_path}")
                    
                except Exception as e:
                    self.print_result(f"Ошибка исправления {file_path}", False, str(e))
                    self.errors.append(f"Ошибка исправления {file_path}: {e}")
            else:
                self.print_result(f"Файл {file_path}", False, "Файл не найден")
    
    def fix_backend_configuration(self):
        """Исправление конфигурации бэкенда"""
        self.print_header("ИСПРАВЛЕНИЕ КОНФИГУРАЦИИ БЭКЕНДА")
        
        files_to_fix = [
            "backend/render.yaml",
            "backend/docker-compose.yml"
        ]
        
        for file_path in files_to_fix:
            if Path(file_path).exists():
                try:
                    # Создаем резервную копию
                    backup_path = self.backup_file(file_path)
                    if not backup_path:
                        continue
                    
                    # Читаем файл
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Исправляем URL бэкенда
                    content_fixed = content.replace(
                        "localhost:8000",
                        self.correct_config["backend_url"]
                    )
                    
                    # Записываем исправленный файл
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content_fixed)
                    
                    self.print_result(f"Исправлен файл {file_path}", True, f"Резервная копия: {backup_path}")
                    self.fixes_applied.append(f"Исправлен {file_path}")
                    
                except Exception as e:
                    self.print_result(f"Ошибка исправления {file_path}", False, str(e))
                    self.errors.append(f"Ошибка исправления {file_path}: {e}")
            else:
                self.print_result(f"Файл {file_path}", False, "Файл не найден")
    
    def fix_frontend_configuration(self):
        """Исправление конфигурации фронтенда"""
        self.print_header("ИСПРАВЛЕНИЕ КОНФИГУРАЦИИ ФРОНТЕНДА")
        
        files_to_fix = [
            "frontend/_redirects",
            "frontend/assets/js/websocket.js",
            "frontend/assets/js/app.js"
        ]
        
        for file_path in files_to_fix:
            if Path(file_path).exists():
                try:
                    # Создаем резервную копию
                    backup_path = self.backup_file(file_path)
                    if not backup_path:
                        continue
                    
                    # Читаем файл
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Исправляем URL фронтенда
                    content_fixed = content.replace(
                        "localhost:3000",
                        self.correct_config["frontend_url"]
                    )
                    
                    # Записываем исправленный файл
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content_fixed)
                    
                    self.print_result(f"Исправлен файл {file_path}", True, f"Резервная копия: {backup_path}")
                    self.fixes_applied.append(f"Исправлен {file_path}")
                    
                except Exception as e:
                    self.print_result(f"Ошибка исправления {file_path}", False, str(e))
                    self.errors.append(f"Ошибка исправления {file_path}: {e}")
            else:
                self.print_result(f"Файл {file_path}", False, "Файл не найден")
    
    def fix_telegram_bot_configuration(self):
        """Исправление конфигурации Telegram бота"""
        self.print_header("ИСПРАВЛЕНИЕ КОНФИГУРАЦИИ TELEGRAM БОТА")
        
        files_to_fix = [
            "backend/app/config/settings.py",
            "backend/app/utils/telegram.py",
            "backend/app/utils/telegram_validator.py",
            "backend/app/utils/security.py",
            "backend/app/utils/security_enhanced.py",
            "backend/docker-compose.yml"
        ]
        
        for file_path in files_to_fix:
            if Path(file_path).exists():
                try:
                    # Создаем резервную копию
                    backup_path = self.backup_file(file_path)
                    if not backup_path:
                        continue
                    
                    # Читаем файл
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Исправляем токен бота
                    old_token_patterns = [
                        r'TELEGRAM_BOT_TOKEN.*=.*["\']([^"\']+)["\']',
                        r'telegram_bot_token.*=.*["\']([^"\']+)["\']',
                        r'bot_token.*=.*["\']([^"\']+)["\']'
                    ]
                    
                    content_fixed = content
                    for pattern in old_token_patterns:
                        content_fixed = re.sub(
                            pattern,
                            lambda m: m.group(0).replace(m.group(1), self.correct_config["telegram_bot_token"]),
                            content_fixed
                        )
                    
                    # Исправляем username бота
                    content_fixed = content_fixed.replace(
                        "your-bot-username",
                        self.correct_config["telegram_bot_username"]
                    )
                    
                    # Записываем исправленный файл
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content_fixed)
                    
                    self.print_result(f"Исправлен файл {file_path}", True, f"Резервная копия: {backup_path}")
                    self.fixes_applied.append(f"Исправлен {file_path}")
                    
                except Exception as e:
                    self.print_result(f"Ошибка исправления {file_path}", False, str(e))
                    self.errors.append(f"Ошибка исправления {file_path}: {e}")
            else:
                self.print_result(f"Файл {file_path}", False, "Файл не найден")
    
    def fix_cors_configuration(self):
        """Исправление CORS конфигурации"""
        self.print_header("ИСПРАВЛЕНИЕ CORS КОНФИГУРАЦИИ")
        
        cors_files = [
            "backend/app/main.py"
        ]
        
        for file_path in cors_files:
            if Path(file_path).exists():
                try:
                    # Создаем резервную копию
                    backup_path = self.backup_file(file_path)
                    if not backup_path:
                        continue
                    
                    # Читаем файл
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Добавляем Telegram Web App в CORS origins
                    telegram_origins = [
                        "https://web.telegram.org",
                        "https://t.me",
                        "https://frabjous-florentine-c506b0.netlify.app"
                    ]
                    
                    # Ищем существующие CORS origins
                    cors_pattern = r'allow_origins\s*=\s*\[([^\]]*)\]'
                    match = re.search(cors_pattern, content)
                    
                    if match:
                        existing_origins = match.group(1)
                        # Добавляем Telegram origins если их нет
                        for origin in telegram_origins:
                            if origin not in existing_origins:
                                existing_origins += f', "{origin}"'
                        
                        # Заменяем CORS origins
                        content_fixed = re.sub(
                            cors_pattern,
                            f'allow_origins = [{existing_origins}]',
                            content
                        )
                        
                        # Записываем исправленный файл
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content_fixed)
                        
                        self.print_result(f"Исправлен CORS в {file_path}", True, f"Резервная копия: {backup_path}")
                        self.fixes_applied.append(f"Исправлен CORS в {file_path}")
                    else:
                        self.print_result(f"CORS не найден в {file_path}", False, "Не удалось найти CORS конфигурацию")
                        
                except Exception as e:
                    self.print_result(f"Ошибка исправления CORS в {file_path}", False, str(e))
                    self.errors.append(f"Ошибка исправления CORS в {file_path}: {e}")
            else:
                self.print_result(f"Файл {file_path}", False, "Файл не найден")
    
    def generate_fix_report(self):
        """Генерация отчета об исправлениях"""
        self.print_header("ОТЧЕТ ОБ ИСПРАВЛЕНИЯХ")
        
        total_fixes = len(self.fixes_applied)
        total_errors = len(self.errors)
        
        print(f"📊 Статистика исправлений:")
        print(f"   ✅ Успешных исправлений: {total_fixes}")
        print(f"   ❌ Ошибок: {total_errors}")
        
        if total_fixes > 0:
            print(f"\n✅ УСПЕШНО ИСПРАВЛЕНО:")
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        
        if total_errors > 0:
            print(f"\n❌ ОШИБКИ:")
            for error in self.errors:
                print(f"   • {error}")
        
        # Сохраняем отчет
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_fixes": total_fixes,
            "total_errors": total_errors,
            "fixes_applied": self.fixes_applied,
            "errors": self.errors
        }
        
        with open('fix_report.json', 'w', encoding='utf-8') as f:
            import json
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 Отчет сохранен в: fix_report.json")
        
        return total_errors == 0
    
    def run_all_fixes(self):
        """Запуск всех исправлений"""
        print("🚀 ЗАПУСК АВТОМАТИЧЕСКИХ ИСПРАВЛЕНИЙ КОНФИГУРАЦИИ СИСТЕМЫ PAX")
        print("=" * 80)
        
        self.fix_database_configuration()
        self.fix_backend_configuration()
        self.fix_frontend_configuration()
        self.fix_telegram_bot_configuration()
        self.fix_cors_configuration()
        
        return self.generate_fix_report()

def main():
    """Основная функция"""
    fixer = SystemConfigurationFixer()
    success = fixer.run_all_fixes()
    
    if success:
        print(f"\n🎉 ВСЕ ИСПРАВЛЕНИЯ ВЫПОЛНЕНЫ УСПЕШНО!")
        print(f"✅ Конфигурация системы приведена в соответствие")
    else:
        print(f"\n⚠️  ИСПРАВЛЕНИЯ ВЫПОЛНЕНЫ С ОШИБКАМИ!")
        print(f"🔧 Проверьте отчет для деталей")

if __name__ == "__main__":
    main() 