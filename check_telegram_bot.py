#!/usr/bin/env python3
"""
Скрипт для проверки статуса Telegram бота
"""

import requests
import json

# Токен бота
BOT_TOKEN = "8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA"

def check_bot_status():
    """Проверка статуса бота"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok'):
            bot_info = data['result']
            print("✅ Бот активен")
            print(f"ID: {bot_info['id']}")
            print(f"Имя: {bot_info['first_name']}")
            print(f"Username: {bot_info.get('username', 'Не установлен')}")
            print(f"Может присоединяться к группам: {bot_info.get('can_join_groups', False)}")
            print(f"Может читать все групповые сообщения: {bot_info.get('can_read_all_group_messages', False)}")
            print(f"Поддерживает встроенные режимы: {bot_info.get('supports_inline_queries', False)}")
            return True
        else:
            print(f"❌ Ошибка бота: {data.get('description', 'Неизвестная ошибка')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def check_webhook_info():
    """Проверка информации о webhook"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok'):
            webhook_info = data['result']
            print("\n📡 Информация о Webhook:")
            print(f"URL: {webhook_info.get('url', 'Не установлен')}")
            print(f"Имеет сертификат: {webhook_info.get('has_custom_certificate', False)}")
            print(f"Ожидающие обновления: {webhook_info.get('pending_update_count', 0)}")
            print(f"Последняя ошибка: {webhook_info.get('last_error_message', 'Нет ошибок')}")
            return True
        else:
            print(f"❌ Ошибка получения webhook: {data.get('description', 'Неизвестная ошибка')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def check_menu_button():
    """Проверка кнопки меню"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMenuButton"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok'):
            menu_info = data['result']
            print("\n🔘 Информация о кнопке меню:")
            print(f"Тип: {menu_info.get('type', 'Не установлен')}")
            if menu_info.get('type') == 'web_app':
                web_app = menu_info.get('web_app', {})
                print(f"Текст: {menu_info.get('text', 'Не установлен')}")
                print(f"URL: {web_app.get('url', 'Не установлен')}")
            return True
        else:
            print(f"❌ Ошибка получения меню: {data.get('description', 'Неизвестная ошибка')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def set_menu_button():
    """Установка кнопки меню"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setChatMenuButton"
    
    # URL вашего приложения
    web_app_url = "https://frabjous-florentine-c506b0.netlify.app"
    
    payload = {
        "menu_button": {
            "type": "web_app",
            "text": "Открыть приложение",
            "web_app": {
                "url": web_app_url
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if data.get('ok'):
            print(f"\n✅ Кнопка меню установлена для URL: {web_app_url}")
            return True
        else:
            print(f"❌ Ошибка установки меню: {data.get('description', 'Неизвестная ошибка')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def main():
    """Основная функция"""
    print("🔍 Проверка статуса Telegram бота...")
    print("=" * 50)
    
    # Проверяем статус бота
    bot_ok = check_bot_status()
    
    if bot_ok:
        # Проверяем webhook
        check_webhook_info()
        
        # Проверяем кнопку меню
        check_menu_button()
        
        # Предлагаем установить кнопку меню
        print("\n" + "=" * 50)
        response = input("Установить кнопку меню для приложения? (y/n): ")
        if response.lower() == 'y':
            set_menu_button()
    else:
        print("❌ Бот не работает. Проверьте токен и настройки.")

if __name__ == "__main__":
    main() 