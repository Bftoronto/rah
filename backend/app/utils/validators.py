import re

def validate_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))

def validate_username(username: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9_]{3,32}$", username)) 