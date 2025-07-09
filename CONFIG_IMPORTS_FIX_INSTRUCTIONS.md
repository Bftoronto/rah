# 🔧 Исправление проблем с импортами конфигурации

## 🚨 Проблема

Ошибка при запуске приложения:
```
ModuleNotFoundError: No module named 'app.config_simple'
```

## ✅ Решение

### Автоматическое исправление

Запустите скрипт исправления:
```bash
./fix_config_imports.sh <server_ip> [ssh_key_path]
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

3. **Исправьте импорты в файлах:**
   ```bash
   # database.py
   sed -i 's/from \.config_simple import settings/from .config.settings import settings/' app/database.py
   
   # notification_service.py
   sed -i 's/from \.\.config_simple import settings/from ..config.settings import settings/' app/services/notification_service.py
   
   # moderation_service.py
   sed -i 's/from \.\.config_simple import settings/from ..config.settings import settings/' app/services/moderation_service.py
   ```

4. **Перезапустите сервис:**
   ```bash
   systemctl restart pax-backend
   ```

5. **Проверьте статус:**
   ```bash
   systemctl status pax-backend
   curl http://localhost:8000/health
   ```

## 📋 Что было исправлено

- ✅ Исправлены импорты `config_simple` на `config.settings`
- ✅ Обновлены файлы: `database.py`, `notification_service.py`, `moderation_service.py`
- ✅ Перезапущен backend сервис

## 🔍 Проверка

После исправления приложение должно запуститься без ошибок:
```bash
curl http://<server_ip>/health
```

## 📝 Причина проблемы

Проблема возникла из-за реорганизации структуры конфигурации:
- **Старый путь:** `app.config_simple`
- **Новый путь:** `app.config.settings`

Файлы, которые ссылались на старый путь, не были обновлены.

**Готово! 🎉** 