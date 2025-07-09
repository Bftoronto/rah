# 🚀 Развертывание PAX на продакшен сервер

## 📋 Требования

### Сервер
- **OS:** Ubuntu 20.04+ или Debian 11+
- **RAM:** Минимум 2GB (рекомендуется 4GB+)
- **Storage:** Минимум 20GB
- **Network:** Статический IP адрес
- **SSH:** Доступ по SSH ключу

### Подготовка
- IP адрес сервера
- SSH приватный ключ
- Домен (опционально, для SSL)
- Telegram Bot Token

## 🔧 Пошаговое развертывание

### Шаг 1: Развертывание приложения

```bash
# Развертывание на сервер
./deploy_production.sh <server_ip> [ssh_key_path]

# Пример:
./deploy_production.sh 192.168.1.100 ~/.ssh/id_rsa
```

**Что происходит:**
- ✅ Установка Python 3.8+, PostgreSQL, Redis, Nginx
- ✅ Создание базы данных и пользователей
- ✅ Настройка systemd сервисов
- ✅ Развертывание кода приложения
- ✅ Применение миграций базы данных
- ✅ Настройка Nginx конфигурации

### Шаг 2: Настройка SSL и домена (рекомендуется)

```bash
# Настройка SSL сертификата
./setup_ssl_domain.sh <server_ip> <domain> [ssh_key_path]

# Пример:
./setup_ssl_domain.sh 192.168.1.100 myapp.com ~/.ssh/id_rsa
```

**Что происходит:**
- ✅ Обновление Nginx конфигурации для домена
- ✅ Получение SSL сертификата от Let's Encrypt
- ✅ Настройка автоматического обновления SSL
- ✅ Обновление CORS настроек

### Шаг 3: Настройка Telegram бота

```bash
# Настройка Telegram бота
./setup_telegram_bot.sh <server_ip> <bot_token> <domain> [ssh_key_path]

# Пример:
./setup_telegram_bot.sh 192.168.1.100 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz myapp.com ~/.ssh/id_rsa
```

**Что происходит:**
- ✅ Обновление .env файла с токеном бота
- ✅ Настройка webhook URL
- ✅ Установка webhook в Telegram API
- ✅ Перезапуск backend сервиса

## 🔍 Проверка развертывания

### Проверка сервисов
```bash
# Проверка статуса всех сервисов
./server_maintenance.sh <server_ip> [ssh_key_path]
```

### Ручная проверка
```bash
# Подключение к серверу
ssh root@<server_ip>

# Проверка сервисов
systemctl status pax-backend
systemctl status nginx
systemctl status postgresql
systemctl status redis-server

# Проверка API
curl http://localhost:8000/health
curl http://localhost:8000/api/docs
```

## ⚙️ Настройка после развертывания

### 1. Обновление .env файла

Отредактируйте `/opt/pax-app/backend/.env`:

```bash
# Подключение к серверу
ssh root@<server_ip>

# Редактирование .env
nano /opt/pax-app/backend/.env
```

**Важные настройки:**
```env
# Безопасность - ОБЯЗАТЕЛЬНО ИЗМЕНИТЕ!
SECRET_KEY=your-super-secret-production-key-change-this-immediately

# Telegram - ДОБАВЬТЕ ВАШ ТОКЕН
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here

# CORS - НАСТРОЙТЕ ВАШ ДОМЕН
CORS_ORIGINS=https://your-domain.com,https://web.telegram.org

# База данных - НЕ ИЗМЕНЯЙТЕ
DATABASE_URL=postgresql://pax_user:pax_secure_password_2024@localhost:5432/pax_db
```

### 2. Перезапуск сервисов

```bash
# После изменения .env
systemctl restart pax-backend
systemctl restart nginx
```

### 3. Настройка DNS

Настройте DNS записи у вашего провайдера:
```
A    your-domain.com     -> <server_ip>
A    www.your-domain.com -> <server_ip>
```

## 📊 Мониторинг и обслуживание

### Автоматический мониторинг
```bash
# Запуск мониторинга
./server_maintenance.sh <server_ip> [ssh_key_path]
```

### Полезные команды
```bash
# Просмотр логов backend
sudo journalctl -u pax-backend -f

# Просмотр логов nginx
sudo tail -f /var/log/nginx/access.log

# Перезапуск сервисов
sudo systemctl restart pax-backend
sudo systemctl restart nginx

# Обновление системы
sudo apt update && sudo apt upgrade -y
```

## 🔒 Безопасность

### Рекомендуемые настройки
1. **Измените пароли по умолчанию:**
   ```bash
   # Изменение пароля PostgreSQL
   sudo -u postgres psql -c "ALTER USER pax_user PASSWORD 'new_secure_password';"
   ```

2. **Настройте firewall:**
   ```bash
   # Установка UFW
   sudo apt install ufw
   
   # Настройка правил
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

3. **Регулярные обновления:**
   ```bash
   # Автоматические обновления безопасности
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure unattended-upgrades
   ```

## 🚨 Устранение неполадок

### Проблемы с подключением
```bash
# Проверка портов
sudo ss -tuln | grep -E ':(80|443|8000)'

# Проверка firewall
sudo ufw status
```

### Проблемы с базой данных
```bash
# Проверка PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -d pax_db -c "SELECT version();"
```

### Проблемы с SSL
```bash
# Проверка SSL сертификатов
sudo certbot certificates

# Обновление SSL
sudo certbot renew
```

### Проблемы с Telegram ботом
```bash
# Проверка webhook
curl -s "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"

# Удаление webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"
```

## 📈 Масштабирование

### Увеличение производительности
1. **Увеличение RAM:** Обновите план сервера
2. **Кэширование:** Redis уже настроен
3. **Балансировка нагрузки:** Добавьте дополнительные серверы
4. **CDN:** Настройте Cloudflare или аналогичный сервис

### Бэкапы
```bash
# Автоматические бэкапы (настройте cron)
0 2 * * * /usr/bin/pg_dump pax_db > /backups/pax_db_$(date +\%Y\%m\%d).sql
```

## ✅ Чеклист готовности

- [ ] Приложение развернуто и доступно
- [ ] SSL сертификат настроен
- [ ] Telegram бот подключен
- [ ] DNS записи настроены
- [ ] .env файл обновлен
- [ ] Firewall настроен
- [ ] Мониторинг работает
- [ ] Бэкапы настроены

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи: `sudo journalctl -u pax-backend -f`
2. Запустите мониторинг: `./server_maintenance.sh <server_ip>`
3. Проверьте статус сервисов: `systemctl status pax-backend`

**Готово к продакшену! 🎉** 