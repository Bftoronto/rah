# Требования для продакшен-развертывания

## Обзор

Документ содержит все требования и рекомендации для безопасного и эффективного развертывания backend в продакшене.

## Системные требования

### Минимальные требования

- **CPU**: 2 ядра
- **RAM**: 4 GB
- **Storage**: 20 GB SSD
- **Network**: 100 Mbps

### Рекомендуемые требования

- **CPU**: 4+ ядра
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **Network**: 1 Gbps

## Зависимости

### Обязательные сервисы

1. **PostgreSQL 13+**
   - Минимум 2 GB RAM
   - Настроенные индексы
   - Регулярные бэкапы

2. **Redis 6+**
   - Для кэширования и сессий
   - Минимум 1 GB RAM

3. **Nginx**
   - Reverse proxy
   - SSL termination
   - Rate limiting

### Опциональные сервисы

1. **Prometheus + Grafana**
   - Мониторинг метрик
   - Алерты

2. **ELK Stack**
   - Централизованное логирование
   - Анализ логов

## Конфигурация безопасности

### Переменные окружения

```bash
# Обязательные
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-super-secret-key-here
TELEGRAM_BOT_TOKEN=your-bot-token

# Рекомендуемые
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-domain.com,https://web.telegram.org

# Безопасность
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_SPECIAL=true

# Мониторинг
ENABLE_METRICS=true
METRICS_PORT=8001
```

### SSL/TLS

- Обязательный SSL сертификат
- Минимум TLS 1.2
- HSTS headers
- Perfect Forward Secrecy

### Firewall

```bash
# Открытые порты
80   - HTTP (redirect to HTTPS)
443  - HTTPS
8000 - API (internal)
8001 - Metrics (internal)
```

## Конфигурация базы данных

### PostgreSQL

```sql
-- Создание пользователя
CREATE USER pax_user WITH PASSWORD 'secure_password';

-- Создание базы данных
CREATE DATABASE pax_db OWNER pax_user;

-- Настройки производительности
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Применение настроек
SELECT pg_reload_conf();
```

### Индексы

```sql
-- Индексы для производительности
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_rides_date_status ON rides(date, status);
CREATE INDEX idx_rides_from_to ON rides(from_location, to_location);
CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
```

## Конфигурация Nginx

```nginx
upstream pax_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL конфигурация
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    # API
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://pax_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check
    location /health {
        proxy_pass http://pax_backend;
        access_log off;
    }

    # Metrics (internal only)
    location /metrics {
        allow 127.0.0.1;
        deny all;
        proxy_pass http://pax_backend;
    }
}
```

## Мониторинг и алерты

### Метрики для отслеживания

1. **Системные метрики**
   - CPU usage
   - Memory usage
   - Disk usage
   - Network I/O

2. **Прикладные метрики**
   - Request rate
   - Response time
   - Error rate
   - Database connections

3. **Бизнес метрики**
   - Active users
   - Rides created
   - Successful matches

### Алерты

```yaml
# prometheus/alerts.yml
groups:
  - name: pax_alerts
    rules:
      - alert: HighCPUUsage
        expr: system_cpu_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          
      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate"
          
      - alert: DatabaseConnectionIssues
        expr: db_connections_active < 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection issues"
```

## Бэкапы

### Автоматические бэкапы

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="pax_db"

# Database backup
pg_dump $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# File backup
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /app/uploads/

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete
```

### Восстановление

```bash
# Restore database
gunzip -c db_backup_20240101_120000.sql.gz | psql pax_db

# Restore files
tar -xzf files_backup_20240101_120000.tar.gz -C /
```

## CI/CD Pipeline

### GitHub Actions

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements_enhanced.txt
          pytest tests/
          
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          # Deployment script
          ./scripts/deploy.py --environment production
```

## Процедуры развертывания

### 1. Подготовка

```bash
# Обновление кода
git pull origin main

# Установка зависимостей
pip install -r requirements_enhanced.txt

# Проверка конфигурации
python -c "from app.config.settings import get_settings; print('Config OK')"
```

### 2. Миграции

```bash
# Backup перед миграцией
pg_dump pax_db > backup_before_migration.sql

# Выполнение миграций
alembic upgrade head

# Проверка миграций
alembic current
```

### 3. Развертывание

```bash
# Остановка сервиса
sudo systemctl stop pax-backend

# Обновление кода
cp -r app/ /opt/pax-backend/

# Запуск сервиса
sudo systemctl start pax-backend

# Проверка здоровья
curl http://localhost:8000/health
```

### 4. Откат

```bash
# Откат кода
git checkout HEAD~1

# Откат базы данных
psql pax_db < backup_before_migration.sql

# Перезапуск
sudo systemctl restart pax-backend
```

## Чеклист готовности к продакшену

### Безопасность
- [ ] SSL сертификат установлен
- [ ] Firewall настроен
- [ ] Переменные окружения защищены
- [ ] Rate limiting включен
- [ ] CORS настроен правильно

### Производительность
- [ ] База данных оптимизирована
- [ ] Индексы созданы
- [ ] Кэширование настроено
- [ ] Nginx настроен

### Мониторинг
- [ ] Метрики собираются
- [ ] Логи централизованы
- [ ] Алерты настроены
- [ ] Health checks работают

### Бэкапы
- [ ] Автоматические бэкапы настроены
- [ ] Тестовое восстановление выполнено
- [ ] Процедуры восстановления документированы

### Документация
- [ ] API документация актуальна
- [ ] Процедуры развертывания документированы
- [ ] Контакты для экстренных случаев указаны

## Экстренные процедуры

### При недоступности API

1. Проверить логи: `tail -f /var/log/pax-backend/error.log`
2. Проверить статус сервиса: `sudo systemctl status pax-backend`
3. Проверить базу данных: `pg_isready -h localhost`
4. Перезапустить сервис: `sudo systemctl restart pax-backend`

### При проблемах с производительностью

1. Проверить метрики: `curl http://localhost:8001/metrics`
2. Проверить использование ресурсов: `htop`
3. Оптимизировать запросы к БД
4. Увеличить ресурсы при необходимости

### При проблемах с безопасностью

1. Проверить логи на подозрительную активность
2. Обновить секретные ключи
3. Проверить права доступа
4. Уведомить команду безопасности 