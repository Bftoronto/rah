# 🚀 Продакшен развертывание PAX Platform

## 📋 Обзор

Это руководство содержит детальные инструкции для развертывания PAX Platform в продакшен-среде с учетом всех требований безопасности, производительности и масштабируемости.

## 🎯 Требования к продакшен-среде

### Минимальные требования
- **OS**: Ubuntu 20.04+ или Debian 11+
- **RAM**: 4GB (рекомендуется 8GB+)
- **Storage**: 50GB SSD (рекомендуется 100GB+)
- **Network**: Статический IP адрес
- **Backup**: Настроенные бэкапы
- **Monitoring**: Система мониторинга

### Рекомендуемые требования
- **OS**: Ubuntu 22.04 LTS
- **RAM**: 16GB+
- **Storage**: 200GB+ NVMe SSD
- **CPU**: 4+ ядра
- **Network**: Выделенный IP с хорошей пропускной способностью
- **CDN**: Cloudflare или аналогичный сервис
- **SSL**: Wildcard сертификат

## 🔧 Пошаговое развертывание

### Шаг 1: Подготовка сервера

#### Создание пользователя и настройка безопасности
```bash
# Подключение к серверу
ssh root@your-server-ip

# Создание пользователя для приложения
adduser pax --disabled-password --gecos ""
usermod -aG sudo pax

# Настройка SSH ключей
mkdir -p /home/pax/.ssh
cp ~/.ssh/authorized_keys /home/pax/.ssh/
chown -R pax:pax /home/pax/.ssh
chmod 700 /home/pax/.ssh
chmod 600 /home/pax/.ssh/authorized_keys

# Настройка sudo без пароля для pax
echo "pax ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
```

#### Обновление системы и установка базовых пакетов
```bash
# Обновление системы
apt update && apt upgrade -y

# Установка необходимых пакетов
apt install -y curl wget git htop iotop nethogs ufw fail2ban

# Настройка firewall
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow 8000/tcp  # Backend API
ufw enable

# Настройка fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### Шаг 2: Развертывание приложения

#### Автоматическое развертывание
```bash
# Переключение на пользователя pax
su - pax

# Клонирование репозитория
git clone https://github.com/your-repo/pax-platform.git
cd pax-platform

# Запуск автоматического развертывания
./deploy_production.sh localhost
```

#### Ручное развертывание (альтернатива)
```bash
# Установка Python и зависимостей
sudo apt install -y python3.11 python3.11-venv python3.11-dev
sudo apt install -y postgresql postgresql-contrib redis-server nginx

# Создание виртуального окружения
python3.11 -m venv /opt/pax-app/venv
source /opt/pax-app/venv/bin/activate

# Установка зависимостей
pip install -r backend/requirements.txt

# Настройка базы данных
sudo -u postgres createdb pax_db
sudo -u postgres createuser pax_user
sudo -u postgres psql -c "ALTER USER pax_user PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE pax_db TO pax_user;"

# Применение миграций
cd backend
alembic upgrade head
```

### Шаг 3: Настройка конфигурации

#### Создание .env файла
```bash
# Создание .env файла
nano /opt/pax-app/backend/.env
```

**Содержимое .env файла:**
```env
# Основные настройки
APP_NAME=PAX Platform
VERSION=1.14.0
DEBUG=false
ENVIRONMENT=production

# Безопасность - ОБЯЗАТЕЛЬНО ИЗМЕНИТЕ!
SECRET_KEY=your-super-secret-production-key-change-this-immediately
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# База данных
DATABASE_URL=postgresql://pax_user:secure_password@localhost:5432/pax_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://localhost:6379

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
TELEGRAM_BOT_USERNAME=pax_rides_bot

# CORS
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com,https://web.telegram.org

# Логирование
LOG_LEVEL=INFO
LOG_FILE=/opt/pax-app/logs/app.log
LOG_FORMAT=json

# Загрузка файлов
UPLOAD_DIR=/opt/pax-app/uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=["image/jpeg","image/png","image/gif","application/pdf"]

# Мониторинг
ENABLE_METRICS=true
METRICS_PORT=9090

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

#### Настройка systemd сервисов
```bash
# Создание сервиса для backend
sudo nano /etc/systemd/system/pax-backend.service
```

**Содержимое pax-backend.service:**
```ini
[Unit]
Description=PAX Platform Backend
After=network.target postgresql.service redis-server.service

[Service]
Type=exec
User=pax
Group=pax
WorkingDirectory=/opt/pax-app/backend
Environment=PATH=/opt/pax-app/venv/bin
ExecStart=/opt/pax-app/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Активация сервиса
sudo systemctl daemon-reload
sudo systemctl enable pax-backend
sudo systemctl start pax-backend
```

### Шаг 4: Настройка Nginx

#### Создание конфигурации Nginx
```bash
# Создание конфигурации сайта
sudo nano /etc/nginx/sites-available/pax-app
```

**Содержимое конфигурации:**
```nginx
# Upstream для backend
upstream pax_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

# HTTP сервер (редирект на HTTPS)
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS сервер
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL конфигурация
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Безопасность
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://web.telegram.org; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;" always;

    # Frontend
    location / {
        root /opt/pax-app/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Кэширование статических файлов
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Vary "Accept-Encoding";
        }
    }

    # API прокси
    location /api/ {
        proxy_pass http://pax_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    }

    # Загрузки
    location /uploads/ {
        alias /opt/pax-app/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Health check
    location /health {
        proxy_pass http://pax_backend;
        access_log off;
    }

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
}
```

```bash
# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/pax-app /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Шаг 5: Настройка SSL

#### Автоматическая настройка с Let's Encrypt
```bash
# Установка Certbot
sudo apt install -y certbot python3-certbot-nginx

# Получение SSL сертификата
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Автоматическое обновление
sudo crontab -e
# Добавить строку:
0 12 * * * /usr/bin/certbot renew --quiet --post-hook "systemctl reload nginx"
```

#### Ручная настройка (для корпоративных сертификатов)
```bash
# Копирование сертификатов
sudo cp your-cert.pem /etc/ssl/certs/
sudo cp your-key.pem /etc/ssl/private/

# Обновление конфигурации Nginx
sudo nano /etc/nginx/sites-available/pax-app
# Обновите пути к сертификатам
```

### Шаг 6: Настройка мониторинга

#### Установка Prometheus и Grafana
```bash
# Установка Prometheus
sudo apt install -y prometheus node-exporter

# Конфигурация Prometheus
sudo nano /etc/prometheus/prometheus.yml
```

**Содержимое prometheus.yml:**
```yaml
global:
  scrape_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'pax-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - localhost:9093
```

```bash
# Установка Grafana
sudo apt install -y grafana

# Настройка автозапуска
sudo systemctl enable prometheus node-exporter grafana-server
sudo systemctl start prometheus node-exporter grafana-server
```

### Шаг 7: Настройка бэкапов

#### Создание скрипта бэкапа
```bash
# Создание скрипта
sudo nano /opt/backup_pax.sh
```

**Содержимое backup_pax.sh:**
```bash
#!/bin/bash

# Настройки
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/pax"
RETENTION_DAYS=30
LOG_FILE="/var/log/pax-backup.log"

# Создание директории
mkdir -p $BACKUP_DIR

# Логирование
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

log "Начало бэкапа"

# Бэкап базы данных
log "Бэкап базы данных..."
pg_dump pax_db > $BACKUP_DIR/pax_db_$DATE.sql
if [ $? -eq 0 ]; then
    log "Бэкап БД успешен"
else
    log "ОШИБКА: Бэкап БД не удался"
    exit 1
fi

# Бэкап файлов
log "Бэкап файлов..."
tar -czf $BACKUP_DIR/pax_files_$DATE.tar.gz /opt/pax-app/ --exclude=/opt/pax-app/venv --exclude=/opt/pax-app/logs
if [ $? -eq 0 ]; then
    log "Бэкап файлов успешен"
else
    log "ОШИБКА: Бэкап файлов не удался"
    exit 1
fi

# Удаление старых бэкапов
log "Удаление старых бэкапов..."
find $BACKUP_DIR -name "*.sql" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Проверка размера бэкапов
BACKUP_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
log "Размер бэкапов: $BACKUP_SIZE"

log "Бэкап завершен успешно"
```

```bash
# Установка прав
sudo chmod +x /opt/backup_pax.sh

# Добавление в cron (ежедневно в 2:00)
echo "0 2 * * * /opt/backup_pax.sh" | sudo crontab -

# Создание директории для бэкапов
sudo mkdir -p /backups/pax
sudo chown pax:pax /backups/pax
```

## 🔒 Безопасность

### Настройка firewall
```bash
# Дополнительные правила firewall
sudo ufw allow from 10.0.0.0/8 to any port 22  # SSH только из внутренней сети
sudo ufw allow from 192.168.0.0/16 to any port 22
sudo ufw deny 22  # Блокировка SSH извне

# Проверка статуса
sudo ufw status verbose
```

### Настройка fail2ban
```bash
# Конфигурация fail2ban
sudo nano /etc/fail2ban/jail.local
```

**Содержимое jail.local:**
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
logpath = /var/log/nginx/access.log
maxretry = 5
```

```bash
# Перезапуск fail2ban
sudo systemctl restart fail2ban
```

### Безопасность базы данных
```bash
# Ограничение доступа к PostgreSQL
sudo nano /etc/postgresql/13/main/pg_hba.conf
```

**Добавьте строки:**
```
# Ограничение доступа только для локального пользователя
local   pax_db        pax_user                                md5
host    pax_db        pax_user        127.0.0.1/32           md5
host    pax_db        pax_user        ::1/128                 md5
# Отключение доступа для всех остальных
local   all           all                                     reject
host    all           all             0.0.0.0/0               reject
```

```bash
# Перезапуск PostgreSQL
sudo systemctl restart postgresql
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