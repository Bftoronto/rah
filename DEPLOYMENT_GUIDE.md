# 🚀 Руководство по развертыванию PAX Platform

## 📋 Обзор

Это руководство содержит пошаговые инструкции для развертывания PAX Platform на различных окружениях - от демонстрации инвесторам до продакшен-среды.

## 🎯 Варианты развертывания

### Вариант 1: Быстрая демонстрация (рекомендуется для инвесторов)

#### Требования
- VPS с Ubuntu 20.04+
- Домен (опционально)
- Telegram Bot Token

#### Пошаговое развертывание

##### 1. Подготовка сервера
```bash
# Подключение к серверу
ssh -i your_key.pem user@your-server-ip

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install nginx certbot python3-certbot-nginx -y
```

##### 2. Автоматическое развертывание
```bash
# Загрузка скрипта развертывания
wget https://raw.githubusercontent.com/your-repo/pax-platform/main/deploy_production.sh
chmod +x deploy_production.sh

# Запуск автоматического развертывания
./deploy_production.sh your-server-ip
```

##### 3. Настройка домена и SSL
```bash
# Настройка SSL сертификата
./setup_ssl_domain.sh your-server-ip your-domain.com

# Настройка Telegram бота
./setup_telegram_bot.sh your-server-ip YOUR_BOT_TOKEN your-domain.com
```

##### 4. Проверка работоспособности
```bash
# Проверка API
curl https://your-domain.com/api/health

# Проверка frontend
curl https://your-domain.com

# Проверка Telegram бота
curl -s "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### Вариант 2: Продакшен развертывание

#### Требования к серверу
- **OS**: Ubuntu 20.04+ или Debian 11+
- **RAM**: Минимум 4GB (рекомендуется 8GB+)
- **Storage**: Минимум 50GB SSD
- **Network**: Статический IP адрес
- **Backup**: Настроенные бэкапы

#### Пошаговое развертывание

##### 1. Подготовка окружения
```bash
# Создание пользователя для приложения
sudo adduser pax --disabled-password --gecos ""
sudo usermod -aG sudo pax

# Настройка SSH ключей
sudo mkdir -p /home/pax/.ssh
sudo cp ~/.ssh/authorized_keys /home/pax/.ssh/
sudo chown -R pax:pax /home/pax/.ssh
sudo chmod 700 /home/pax/.ssh
sudo chmod 600 /home/pax/.ssh/authorized_keys
```

##### 2. Развертывание приложения
```bash
# Переключение на пользователя pax
sudo su - pax

# Клонирование репозитория
git clone https://github.com/your-repo/pax-platform.git
cd pax-platform

# Запуск автоматического развертывания
./deploy_production.sh localhost
```

##### 3. Настройка мониторинга
```bash
# Установка мониторинга
sudo apt install prometheus node-exporter grafana -y

# Настройка алертов
sudo cp monitoring/prometheus.yml /etc/prometheus/
sudo systemctl enable prometheus node-exporter grafana-server
sudo systemctl start prometheus node-exporter grafana-server
```

##### 4. Настройка бэкапов
```bash
# Создание скрипта бэкапа
sudo nano /opt/backup_pax.sh

# Содержимое скрипта:
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/pax"
mkdir -p $BACKUP_DIR

# Бэкап базы данных
pg_dump pax_db > $BACKUP_DIR/pax_db_$DATE.sql

# Бэкап файлов
tar -czf $BACKUP_DIR/pax_files_$DATE.tar.gz /opt/pax-app/

# Удаление старых бэкапов (старше 30 дней)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Установка прав
chmod +x /opt/backup_pax.sh

# Добавление в cron (ежедневно в 2:00)
echo "0 2 * * * /opt/backup_pax.sh" | sudo crontab -
```

### Вариант 3: Docker развертывание

#### Создание Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://pax_user:pax_password@db:5432/pax_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs

  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=pax_db
      - POSTGRES_USER=pax_user
      - POSTGRES_PASSWORD=pax_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### Запуск
```bash
# Сборка и запуск
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f backend
```

## 🔧 Настройка после развертывания

### 1. Конфигурация приложения

#### Обновление .env файла
```bash
# Подключение к серверу
ssh pax@your-server-ip

# Редактирование конфигурации
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

# Redis - для кэширования
REDIS_URL=redis://localhost:6379

# Логирование
LOG_LEVEL=INFO
LOG_FILE=/opt/pax-app/logs/app.log

# Загрузка файлов
UPLOAD_DIR=/opt/pax-app/uploads
MAX_FILE_SIZE=10485760  # 10MB
```

### 2. Настройка DNS

Настройте DNS записи у вашего провайдера:
```
A    your-domain.com     -> <server_ip>
A    www.your-domain.com -> <server_ip>
CNAME api.your-domain.com -> your-domain.com
```

### 3. Настройка SSL сертификатов

#### Автоматическая настройка (Let's Encrypt)
```bash
# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet
```

#### Ручная настройка (для корпоративных сертификатов)
```bash
# Копирование сертификатов
sudo cp your-cert.pem /etc/ssl/certs/
sudo cp your-key.pem /etc/ssl/private/

# Обновление Nginx конфигурации
sudo nano /etc/nginx/sites-available/pax-app
```

### 4. Настройка Telegram бота

#### Создание бота
1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Введите название: "PAX - Поиск попутчиков"
4. Введите username: "pax_rides_bot"
5. Сохраните токен

#### Настройка Web App
```bash
# В @BotFather:
1. /mybots
2. Выберите созданного бота
3. Bot Settings → Menu Button
4. URL: https://your-domain.com
5. Сохраните настройки
```

#### Настройка webhook
```bash
# Установка webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/api/telegram/webhook",
    "allowed_updates": ["message", "callback_query"]
  }'

# Проверка webhook
curl -s "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

## 📊 Мониторинг и обслуживание

### Автоматический мониторинг
```bash
# Запуск мониторинга
./server_maintenance.sh your-server-ip
```

### Полезные команды
```bash
# Просмотр логов backend
sudo journalctl -u pax-backend -f

# Просмотр логов nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Перезапуск сервисов
sudo systemctl restart pax-backend
sudo systemctl restart nginx

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Проверка дискового пространства
df -h

# Проверка использования памяти
free -h

# Проверка загрузки CPU
htop
```

### Мониторинг производительности
```bash
# Установка дополнительных инструментов
sudo apt install htop iotop nethogs -y

# Мониторинг в реальном времени
htop
iotop
nethogs
```

## 🔒 Безопасность

### Настройка firewall
```bash
# Установка UFW
sudo apt install ufw

# Настройка правил
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 8000/tcp  # Backend API
sudo ufw enable

# Проверка статуса
sudo ufw status
```

### Обновление системы
```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Настройка автоматических перезагрузок
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
# Раскомментируйте строку:
# Unattended-Upgrade::Automatic-Reboot "true";
```

### Безопасность базы данных
```bash
# Изменение паролей по умолчанию
sudo -u postgres psql -c "ALTER USER pax_user PASSWORD 'new_secure_password';"

# Ограничение доступа к PostgreSQL
sudo nano /etc/postgresql/13/main/pg_hba.conf
# Добавьте строки:
# local   pax_db        pax_user                                md5
# host    pax_db        pax_user        127.0.0.1/32           md5

# Перезапуск PostgreSQL
sudo systemctl restart postgresql
```

## 🚨 Устранение неполадок

### Проблемы с подключением
```bash
# Проверка портов
sudo ss -tuln | grep -E ':(80|443|8000)'

# Проверка firewall
sudo ufw status

# Проверка nginx
sudo nginx -t
sudo systemctl status nginx
```

### Проблемы с базой данных
```bash
# Проверка PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -d pax_db -c "SELECT version();"

# Проверка подключений
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### Проблемы с SSL
```bash
# Проверка SSL сертификатов
sudo certbot certificates

# Обновление SSL
sudo certbot renew

# Проверка SSL соединения
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

### Проблемы с Telegram ботом
```bash
# Проверка webhook
curl -s "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"

# Удаление webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook"

# Установка webhook заново
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/api/telegram/webhook"}'
```

### Проблемы с производительностью
```bash
# Проверка использования ресурсов
top
htop
iotop

# Проверка логов производительности
sudo journalctl -u pax-backend --since "1 hour ago" | grep "performance"

# Оптимизация PostgreSQL
sudo -u postgres psql -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 📈 Масштабирование

### Увеличение производительности
1. **Увеличение RAM**: Обновите план сервера
2. **Кэширование**: Redis уже настроен
3. **Балансировка нагрузки**: Добавьте дополнительные серверы
4. **CDN**: Настройте Cloudflare или аналогичный сервис

### Горизонтальное масштабирование
```bash
# Настройка load balancer
sudo apt install haproxy

# Конфигурация HAProxy
sudo nano /etc/haproxy/haproxy.cfg
```

### Вертикальное масштабирование
```bash
# Увеличение ресурсов сервера
# Обновите план у вашего провайдера

# Оптимизация PostgreSQL
sudo nano /etc/postgresql/13/main/postgresql.conf
# Увеличьте значения:
# shared_buffers = 256MB
# effective_cache_size = 1GB
# work_mem = 4MB
```

## ✅ Чеклист готовности

### Техническая готовность
- [ ] Приложение развернуто и доступно
- [ ] SSL сертификат настроен
- [ ] Telegram бот подключен
- [ ] DNS записи настроены
- [ ] .env файл обновлен
- [ ] Firewall настроен
- [ ] Мониторинг работает
- [ ] Бэкапы настроены

### Бизнес-готовность
- [ ] Демо-данные загружены
- [ ] Тестовые пользователи созданы
- [ ] Презентация подготовлена
- [ ] Метрики настроены
- [ ] Поддержка готова

### Безопасность
- [ ] Пароли изменены
- [ ] SSL настроен
- [ ] Firewall активен
- [ ] Обновления автоматизированы
- [ ] Бэкапы тестированы

## 🆘 Поддержка

При возникновении проблем:

1. **Проверьте логи**: `sudo journalctl -u pax-backend -f`
2. **Запустите мониторинг**: `./server_maintenance.sh your-server-ip`
3. **Проверьте статус сервисов**: `sudo systemctl status pax-backend`

### Контакты поддержки
- 📧 **Email**: support@pax-platform.com
- 📱 **Telegram**: @pax_support_bot
- 📚 **Документация**: [docs.pax-platform.com](https://docs.pax-platform.com)

---

**Готово к продакшену! 🎉**

Платформа PAX полностью развернута и готова для коммерческого использования. 