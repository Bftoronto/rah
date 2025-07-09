# 📋 ИНСТРУКЦИИ ДЛЯ РУЧНОГО ЗАВЕРШЕНИЯ МИГРАЦИИ

## 🚨 Текущая ситуация

**Проблема:** Не удается подключиться к серверу Selectel по SSH
**Решение:** Ручное завершение миграции на сервере
**Статус:** Локальная подготовка завершена ✅

## 📁 Подготовленные файлы

### Резервные копии созданы:
- `backups/[timestamp]/code_backup.tar.gz` - Резервная копия кода
- `backups/[timestamp]/environment_backup.txt` - Переменные окружения
- `migration_scripts/` - Все скрипты миграции

### SSH ключи созданы:
- `~/.ssh/id_rsa_selectel` - Приватный ключ
- `~/.ssh/id_rsa_selectel.pub` - Публичный ключ

## 🔧 Шаги для завершения миграции

### Шаг 1: Получить доступ к серверу

#### Вариант A: Через панель управления Selectel
1. Войти в https://my.selectel.ru/
2. Найти сервер 31.41.155.88
3. Использовать веб-консоль или VNC
4. Войти как root

#### Вариант B: Через SSH с паролем
```bash
# Если есть пароль от сервера
ssh root@31.41.155.88
```

#### Вариант C: Через техническую поддержку
1. Связаться с support@selectel.ru
2. Попросить настроить SSH ключи
3. Предоставить публичный ключ

### Шаг 2: Добавить SSH ключ на сервер

#### Через панель управления:
1. Войти в панель управления Selectel
2. Перейти в настройки сервера
3. Найти раздел SSH Keys
4. Добавить публичный ключ:
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDfLnAOru8aKTciq2M1disxNnrMxi+5WkNvYt+hGg7R8HUunoMnokcXcgtBBnD+1cM6nCX2g8SS1J44wS19VRf1PjdsqVyD4bqGiCI1DtR++u62/c/q8Jsj+5dyU/ED8bhYzrBzkx9mxvbZpPNgpsiH9rPrrJMbFCTuiMwxldYf8mrCTsVP6ddp8DMpFGSukZxMAu0PU2DOeo/oy24VoKLqpv2JuycvM5OtkwCskci2ArttBdTR/hZCO4U7XH36IFkNkAtpsnz6XG+BblMtbYT57luFFeQELP+K5RRvEmQ7IEGab2jyF9YRQ2eIBHnwxKqqa8WtoKI51rHqEl1mYJmj7XprmVw8xiqj6qdqBaRUJm92TaJxvjEsfpGEAWvnyM4NiBbpmYLvUdbZRyKjeV5RFUF8Na6bgEPEAY3e5njWUuqwkH/YNn3Xi63CA5IxbGRLdN0TrAKWYAZkWFG4/pnjV95hE7OfgIEg2BodPMtKTzYjnpfj4/7zmmW2YGq56Kci2Lm3FLLOsulvl//r73vYCBv34J4E9zE1sZk4gsUx/5r6bAKpr8IlDEL9Ja08fPJHCJFtzMSiwOFVZMcO4R6OEjN3hYFOTaX3oVvxtoCMR6irgjm+nTqN3jmoqqLwOI8m2e5xs2vqzotNWBj5PlIEJN/qf61fmEwVTPS8IGJShw== migration@selectel
```

#### Через командную строку (если есть доступ):
```bash
# Создать директорию SSH
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Добавить публичный ключ
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDfLnAOru8aKTciq2M1disxNnrMxi+5WkNvYt+hGg7R8HUunoMnokcXcgtBBnD+1cM6nCX2g8SS1J44wS19VRf1PjdsqVyD4bqGiCI1DtR++u62/c/q8Jsj+5dyU/ED8bhYzrBzkx9mxvbZpPNgpsiH9rPrrJMbFCTuiMwxldYf8mrCTsVP6ddp8DMpFGSukZxMAu0PU2DOeo/oy24VoKLqpv2JuycvM5OtkwCskci2ArttBdTR/hZCO4U7XH36IFkNkAtpsnz6XG+BblMtbYT57luFFeQELP+K5RRvEmQ7IEGab2jyF9YRQ2eIBHnwxKqqa8WtoKI51rHqEl1mYJmj7XprmVw8xiqj6qdqBaRUJm92TaJxvjEsfpGEAWvnyM4NiBbpmYLvUdbZRyKjeV5RFUF8Na6bgEPEAY3e5njWUuqwkH/YNn3Xi63CA5IxbGRLdN0TrAKWYAZkWFG4/pnjV95hE7OfgIEg2BodPMtKTzYjnpfj4/7zmmW2YGq56Kci2Lm3FLLOsulvl//r73vYCBv34J4E9zE1sZk4gsUx/5r6bAKpr8IlDEL9Ja08fPJHCJFtzMSiwOFVZMcO4R6OEjN3hYFOTaX3oVvxtoCMR6irgjm+nTqN3jmoqqLwOI8m2e5xs2vqzotNWBj5PlIEJN/qf61fmEwVTPS8IGJShw== migration@selectel" >> ~/.ssh/authorized_keys

# Настроить права доступа
chmod 600 ~/.ssh/authorized_keys
```

### Шаг 3: Подготовка сервера

#### Установка необходимых пакетов:
```bash
# Обновление системы
apt update && apt upgrade -y

# Установка Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Установка Python
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Настройка firewall
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw allow 5432/tcp
ufw allow 6379/tcp
```

#### Создание директорий:
```bash
# Создание директорий приложения
mkdir -p /opt/pax-backend
mkdir -p /opt/pax-backend/uploads
mkdir -p /opt/pax-backend/ssl
mkdir -p /opt/pax-backend/logs
mkdir -p /opt/pax-backend/backups

# Настройка прав доступа
chown -R root:root /opt/pax-backend
chmod -R 755 /opt/pax-backend
```

### Шаг 4: Копирование файлов

#### Создание .env файла:
```bash
cat > /opt/pax-backend/.env << 'EOF'
# База данных
DATABASE_URL=postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain

# Telegram Bot
TELEGRAM_BOT_TOKEN=8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA
TELEGRAM_BOT_USERNAME=paxdemobot

# Безопасность
SECRET_KEY=8f3b2c1e-4a5d-11ee-be56-0242ac120002
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Настройки приложения
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Загрузка файлов
UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif

# CORS
CORS_ORIGINS=https://web.telegram.org,https://t.me,https://frabjous-florentine-c506b0.netlify.app,https://31.41.155.88

# Redis
REDIS_URL=redis://localhost:6379
EOF
```

#### Копирование кода:
```bash
# Распаковка кода (если есть архив)
cd /opt/pax-backend
# tar -xzf /path/to/code_backup.tar.gz

# Или клонирование из репозитория
git clone https://github.com/your-repo/pax-backend.git .
```

### Шаг 5: Настройка Docker

#### Создание docker-compose.yml:
```bash
cat > /opt/pax-backend/docker-compose.yml << 'EOF'
services:
  # База данных PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ridesharing
      POSTGRES_USER: rideshare_user
      POSTGRES_PASSWORD: rideshare_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rideshare_user -d ridesharing"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis для кэширования
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend FastAPI
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://paxmain_user:IUwzoIuzbKG9RuruiHSxBFTllTwaK4DN@dpg-d1lu8jnfte5s73dv6780-a/paxmain
      - REDIS_URL=redis://redis:6379
      - TELEGRAM_BOT_TOKEN=8187393599:AAEudOluahmhNJixt_hW8mvWjWC0eh1YIlA
      - SECRET_KEY=8f3b2c1e-4a5d-11ee-be56-0242ac120002
      - DEBUG=false
      - ENVIRONMENT=production
    volumes:
      - ./app:/app/app
      - ./uploads:/app/uploads
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  # Nginx для проксирования и статики
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./uploads:/usr/share/nginx/html/uploads
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF
```

### Шаг 6: Запуск сервисов

```bash
# Переход в директорию приложения
cd /opt/pax-backend

# Сборка и запуск контейнеров
docker-compose build
docker-compose up -d

# Проверка статуса
docker-compose ps

# Проверка логов
docker-compose logs -f
```

### Шаг 7: Валидация

```bash
# Проверка здоровья API
curl http://localhost:8000/health

# Проверка всех эндпоинтов
curl http://localhost:8000/
curl http://localhost:8000/api/info

# Проверка базы данных
docker-compose exec backend python -c "
import sys
sys.path.append('/app')
from app.database import check_db_connection
print('Database connection:', check_db_connection())
"

# Проверка Redis
docker-compose exec redis redis-cli ping
```

## 📞 Контакты для помощи

### Техническая поддержка Selectel:
- **Email:** support@selectel.ru
- **Телефон:** +7 (800) 555-35-35
- **Чат:** https://selectel.ru/support/

### Внутренние контакты:
- **DevOps инженер:** [Контакт]
- **Системный администратор:** [Контакт]
- **Менеджер проекта:** [Контакт]

## ✅ Критерии успеха

После выполнения всех шагов должны работать:
- ✅ API доступен по адресу http://31.41.155.88:8000
- ✅ Health check возвращает статус "healthy"
- ✅ Все контейнеры запущены и работают
- ✅ База данных подключена
- ✅ Redis работает
- ✅ Nginx проксирует запросы

---

**⚠️ ВАЖНО:** После завершения миграции обязательно протестировать все функции приложения! 