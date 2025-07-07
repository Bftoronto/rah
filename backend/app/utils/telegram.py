import hashlib
import hmac
import time
from typing import Dict

TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"  # Заменить на реальный токен

# Проверка подписи Telegram Login

def check_telegram_auth(data: Dict[str, str]) -> bool:
    auth_data = data.copy()
    hash_ = auth_data.pop('hash')
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(auth_data.items())])
    secret_key = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()
    hmac_string = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac_string == hash_ 