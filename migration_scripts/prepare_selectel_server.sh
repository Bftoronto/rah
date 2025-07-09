#!/bin/bash

# Скрипт подготовки сервера Selectel для миграции
# Выполняется на сервере: ssh root@31.41.155.88

set -e

echo "🚀 Начинаем подготовку сервера Selectel..."

# Обновление системы
echo "📦 Обновление системы..."
apt update && apt upgrade -y

# Установка необходимых пакетов
echo "🔧 Установка базовых пакетов..."
apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    htop \
    nano \
    vim

# Установка Docker
echo "🐳 Установка Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Добавление пользователя в группу docker
usermod -aG docker $USER

# Установка Docker Compose
echo "📦 Установка Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Установка Python 3.11
echo "🐍 Установка Python 3.11..."
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Настройка firewall
echo "🔥 Настройка firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw allow 5432/tcp
ufw allow 6379/tcp

# Создание директорий для приложения
echo "📁 Создание директорий..."
mkdir -p /opt/pax-backend
mkdir -p /opt/pax-backend/uploads
mkdir -p /opt/pax-backend/ssl
mkdir -p /opt/pax-backend/logs
mkdir -p /opt/pax-backend/backups

# Настройка прав доступа
chown -R root:root /opt/pax-backend
chmod -R 755 /opt/pax-backend

# Создание пользователя для приложения
echo "👤 Создание пользователя приложения..."
useradd -r -s /bin/false paxapp
usermod -aG docker paxapp

# Настройка systemd для автозапуска
echo "⚙️ Настройка systemd..."
cat > /etc/systemd/system/pax-backend.service << EOF
[Unit]
Description=Pax Backend Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/pax-backend
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable pax-backend.service

# Настройка логирования
echo "📝 Настройка логирования..."
cat > /etc/logrotate.d/pax-backend << EOF
/opt/pax-backend/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

# Создание скрипта мониторинга
echo "📊 Создание скрипта мониторинга..."
cat > /opt/pax-backend/monitor.sh << 'EOF'
#!/bin/bash

LOG_FILE="/opt/pax-backend/logs/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Проверка Docker контейнеров
if ! docker ps | grep -q "pax-backend"; then
    echo "[$DATE] ERROR: Backend container is down!" >> $LOG_FILE
    systemctl restart pax-backend.service
fi

# Проверка доступности API
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "[$DATE] ERROR: API health check failed!" >> $LOG_FILE
fi

# Проверка дискового пространства
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "[$DATE] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x /opt/pax-backend/monitor.sh

# Добавление в crontab
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/pax-backend/monitor.sh") | crontab -

echo "✅ Подготовка сервера завершена!"
echo "📋 Следующие шаги:"
echo "1. Скопировать код приложения"
echo "2. Настроить environment переменные"
echo "3. Запустить миграцию данных"
echo "4. Протестировать функциональность" 