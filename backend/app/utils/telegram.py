import hashlib
import hmac
import time
import os
from typing import Dict

# Получаем токен из переменных окружения, если не задан — используем дефолтный
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA")

def verify_telegram_auth(auth_data: Dict[str, str]) -> bool:
    """
    Верификация данных Telegram Login
    """
    try:
        hash_ = auth_data.pop('hash')
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(auth_data.items())])
        secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
        hmac_string = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        return hmac_string == hash_
    except Exception as e:
        print(f"Ошибка верификации Telegram: {str(e)}")
        return False 