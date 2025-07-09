# 🔧 Исправление проблемы с Pydantic BaseSettings

## 🚨 Проблема

Ошибка при запуске приложения:
```
pydantic.errors.PydanticImportError: `BaseSettings` has been moved to the `pydantic-settings` package.
```

## ✅ Решение

### Автоматическое исправление

Запустите скрипт исправления:
```bash
./fix_pydantic_issue.sh <server_ip> [ssh_key_path]
```

### Ручное исправление

Если у вас есть доступ к серверу:

1. **Подключитесь к серверу:**
   ```bash
   ssh root@<server_ip>
   ```

2. **Перейдите в директорию приложения:**
   ```bash
   cd /opt/pax-app/backend
   ```

3. **Добавьте зависимость:**
   ```bash
   source venv/bin/activate
   pip install pydantic-settings==2.1.0
   ```

4. **Исправьте импорты в файлах:**
   ```bash
   # settings.py
   sed -i 's/from pydantic import BaseSettings, Field/from pydantic import Field\nfrom pydantic_settings import BaseSettings/' app/config/settings.py
   
   # logging.py
   sed -i 's/from pydantic import BaseSettings, Field/from pydantic import Field\nfrom pydantic_settings import BaseSettings/' app/config/logging.py
   
   # security.py
   sed -i 's/from pydantic import BaseSettings, Field/from pydantic import Field\nfrom pydantic_settings import BaseSettings/' app/config/security.py
   
   # database.py
   sed -i 's/from pydantic import BaseSettings, Field/from pydantic import Field\nfrom pydantic_settings import BaseSettings/' app/config/database.py
   ```

5. **Перезапустите сервис:**
   ```bash
   systemctl restart pax-backend
   ```

6. **Проверьте статус:**
   ```bash
   systemctl status pax-backend
   curl http://localhost:8000/health
   ```

## 📋 Что было исправлено

- ✅ Добавлен пакет `pydantic-settings==2.1.0`
- ✅ Исправлены импорты `BaseSettings` во всех файлах конфигурации
- ✅ Обновлен `requirements.txt`
- ✅ Перезапущен backend сервис

## 🔍 Проверка

После исправления приложение должно запуститься без ошибок:
```bash
curl http://<server_ip>/health
```

**Готово! 🎉** 