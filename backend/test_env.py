#!/usr/bin/env python3
"""
Скрипт для установки тестовых переменных окружения
"""

import os

def set_test_environment():
    """Устанавливает тестовые переменные окружения"""
    test_env = {
        'DATABASE_URL': 'sqlite:///./test.db',
        'SECRET_KEY': 'test_secret_key_for_diagnosis_only',
        'TELEGRAM_BOT_TOKEN': 'test_bot_token',
        'REDIS_URL': 'redis://localhost:6379',
        'UPLOAD_DIR': './uploads',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test'
    }
    
    for key, value in test_env.items():
        os.environ[key] = value
        print(f"✅ Установлена переменная: {key} = {value}")

if __name__ == "__main__":
    set_test_environment() 