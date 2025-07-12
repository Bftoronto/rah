# 🤖 Настройка Telegram бота для PAX Platform

## 📋 Обзор

Это руководство содержит пошаговые инструкции для настройки Telegram бота и интеграции с PAX Platform для полнофункционального сервиса поиска попутчиков.

## 🎯 Требования

### Необходимые компоненты
- **Telegram аккаунт** для создания бота
- **Домен** с SSL сертификатом (обязательно для Web Apps)
- **PAX Platform** развернутая на сервере
- **Доступ к @BotFather** в Telegram

### Технические требования
- **HTTPS протокол** (обязательно для Telegram Web Apps)
- **Валидный SSL сертификат** (Let's Encrypt или коммерческий)
- **CORS настройки** для web.telegram.org
- **Webhook поддержка** на сервере

## 🔧 Пошаговая настройка

### Шаг 1: Создание бота через @BotFather

#### 1.1 Начальная настройка
```bash
# В Telegram найдите @BotFather и отправьте:
/newbot
```

#### 1.2 Настройка бота
```
# Название бота (отображается пользователям):
PAX - Поиск попутчиков

# Username бота (должен заканчиваться на 'bot'):
pax_rides_bot
```

#### 1.3 Сохранение токена
```
# BotFather вернет токен вида:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Сохраните этот токен - он понадобится для настройки
```

### Шаг 2: Настройка Web App

#### 2.1 Создание Web App
```bash
# В @BotFather отправьте:
/newapp
```

#### 2.2 Настройка Web App
```
# Название приложения:
PAX Platform

# Короткое описание:
Сервис поиска попутчиков

# Описание:
Найдите попутчиков для поездки между городами России. 
Бронируйте поездки, находите водителей и экономьте на путешествиях.

# URL приложения:
https://your-domain.com

# Категория:
Travel
```

#### 2.3 Настройка кнопки меню
```bash
# В @BotFather отправьте:
/setmenubutton
```

```
# Выберите вашего бота
# Введите URL:
https://your-domain.com
```

### Шаг 3: Настройка команд бота

#### 3.1 Установка команд
```bash
# В @BotFather отправьте:
/setcommands
```

#### 3.2 Список команд
```
start - Начать поиск попутчиков
search - Поиск поездок
mytrips - Мои поездки
profile - Мой профиль
help - Помощь
settings - Настройки
support - Поддержка
```

### Шаг 4: Настройка описания бота

#### 4.1 Описание бота
```bash
# В @BotFather отправьте:
/setdescription
```

```
# Описание:
PAX - удобный сервис для поиска попутчиков. 
Бронируйте поездки, находите водителей и экономьте на путешествиях.
```

#### 4.2 Информация о боте
```bash
# В @BotFather отправьте:
/setabouttext
```

```
# Информация о боте:
PAX Platform - это современный сервис для поиска попутчиков в России.

Основные возможности:
• Поиск поездок по маршруту и дате
• Бронирование мест с подтверждением
• Система рейтингов и отзывов
• Встроенный чат с водителем
• Безопасные прямые расчеты

Поддерживаемые способы оплаты:
• Наличный расчет
• Перевод на карту через СБП

Безопасность и надежность гарантированы!
```

### Шаг 5: Настройка веб-сервера

#### 5.1 Требования к серверу
```nginx
# Пример конфигурации Nginx для Telegram Web App
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL конфигурация (обязательно)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # CORS для Telegram
    add_header Access-Control-Allow-Origin "https://web.telegram.org" always;
    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    
    # Frontend
    location / {
        root /opt/pax-app/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 5.2 Проверка SSL
```bash
# Проверка SSL сертификата
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Проверка доступности
curl -I https://your-domain.com
```

### Шаг 6: Интеграция с PAX Platform

#### 6.1 Настройка .env файла
```bash
# Редактирование конфигурации
nano /opt/pax-app/backend/.env
```

```env
# Telegram настройки
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
TELEGRAM_BOT_USERNAME=pax_rides_bot

# CORS настройки
CORS_ORIGINS=https://your-domain.com,https://web.telegram.org,https://t.me

# Webhook URL
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/telegram/webhook
```

#### 6.2 Настройка webhook
```bash
# Установка webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/api/telegram/webhook",
    "allowed_updates": ["message", "callback_query", "inline_query"],
    "drop_pending_updates": true
  }'

# Проверка webhook
curl -s "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

#### 6.3 Перезапуск сервисов
```bash
# Перезапуск backend
sudo systemctl restart pax-backend

# Проверка статуса
sudo systemctl status pax-backend
```

## 🧪 Тестирование интеграции

### Тест 1: Проверка Web App
```javascript
// Добавьте в index.html для отладки
console.log('Telegram Web App API:', window.Telegram?.WebApp);
console.log('User:', window.Telegram?.WebApp?.initDataUnsafe?.user);
console.log('Chat:', window.Telegram?.WebApp?.initDataUnsafe?.chat);
```

### Тест 2: Проверка аутентификации
```javascript
// Проверка инициализации Telegram Web App
if (window.Telegram && window.Telegram.WebApp) {
    const tg = window.Telegram.WebApp;
    
    // Инициализация
    tg.ready();
    tg.expand();
    
    // Получение данных пользователя
    const user = tg.initDataUnsafe?.user;
    console.log('User ID:', user?.id);
    console.log('Username:', user?.username);
    console.log('First Name:', user?.first_name);
}
```

### Тест 3: Проверка API
```bash
# Тест API endpoints
curl -X POST "https://your-domain.com/api/auth/telegram/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "init_data": "test_data",
    "user": {
      "id": 123456789,
      "first_name": "Test",
      "username": "test_user"
    }
  }'
```

## 🔧 Функциональность приложения

### Основные экраны
- **Ограничение доступа** - при нулевом балансе
- **Поиск поездок** - форма с полями "откуда", "куда", дата, количество мест
- **Результаты поиска** - список доступных поездок с деталями
- **Профиль водителя** - рейтинг, отзывы, информация о водителе
- **Способы оплаты** - выбор метода пополнения баланса
- **Выбор банка** - для СБП платежей
- **Успешная оплата** - подтверждение бронирования
- **Регистрация** - пошаговая верификация (10 шагов)
- **Профиль пользователя** - баланс, статистика, настройки
- **Мои поездки** - история забронированных и созданных поездок

### API эндпоинты
```javascript
// Основные API методы
const api = {
    // Аутентификация
    verifyTelegram: (initData) => fetch('/api/auth/telegram/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ init_data: initData })
    }),
    
    // Поиск поездок
    searchRides: (params) => fetch('/api/rides/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    }),
    
    // Бронирование
    bookRide: (rideId) => fetch(`/api/rides/${rideId}/book`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
    }),
    
    // Создание поездки
    createRide: (rideData) => fetch('/api/rides/create', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(rideData)
    }),
    
    // Платежи
    processPayment: (amount, method) => fetch('/api/payments/process', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ amount, method })
    }),
    
    // Профиль
    getProfile: () => fetch('/api/profile', {
        headers: { 'Authorization': `Bearer ${token}` }
    }),
    
    // Мои поездки
    getMyRides: () => fetch('/api/rides/my', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
};
```

## 🔒 Безопасность

### Валидация данных Telegram
```javascript
// Проверка подписи данных от Telegram
function validateTelegramData(initData, botToken) {
    const data = new URLSearchParams(initData);
    const hash = data.get('hash');
    data.delete('hash');
    
    // Создание HMAC
    const secret = crypto.createHmac('sha256', 'WebAppData').update(botToken).digest();
    const checkString = Array.from(data.entries())
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([key, value]) => `${key}=${value}`)
        .join('\n');
    
    const hmac = crypto.createHmac('sha256', secret).update(checkString).digest('hex');
    
    return hmac === hash;
}
```

### Защита от CSRF
```javascript
// Добавление CSRF токена к запросам
function addCSRFToken(headers) {
    const token = document.querySelector('meta[name="csrf-token"]')?.content;
    if (token) {
        headers['X-CSRF-Token'] = token;
    }
    return headers;
}
```

### Санитизация данных
```javascript
// Санитизация пользовательского ввода
function sanitizeInput(input) {
    return input.replace(/[<>]/g, '');
}
```

## 📱 Специфика Telegram Web App

### Инициализация
```javascript
// Правильная инициализация Telegram Web App
document.addEventListener('DOMContentLoaded', function() {
    if (window.Telegram && window.Telegram.WebApp) {
        const tg = window.Telegram.WebApp;
        
        // Инициализация
        tg.ready();
        
        // Настройка темы
        tg.setHeaderColor('#2481cc');
        tg.setBackgroundColor('#ffffff');
        
        // Получение данных пользователя
        const user = tg.initDataUnsafe?.user;
        if (user) {
            // Автоматическая авторизация
            handleTelegramAuth(user);
        }
    }
});
```

### Обработка событий
```javascript
// Обработка событий Telegram Web App
window.Telegram.WebApp.onEvent('mainButtonClicked', function() {
    // Обработка нажатия главной кнопки
    handleMainButtonClick();
});

window.Telegram.WebApp.onEvent('backButtonClicked', function() {
    // Обработка нажатия кнопки "Назад"
    handleBackButtonClick();
});

window.Telegram.WebApp.onEvent('settingsButtonClicked', function() {
    // Обработка нажатия кнопки настроек
    handleSettingsClick();
});
```

### Уведомления
```javascript
// Отправка уведомлений через Telegram
function sendTelegramNotification(userId, message) {
    fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            chat_id: userId,
            text: message,
            parse_mode: 'HTML'
        })
    });
}
```

## 🚨 Устранение неполадок

### Проблема: Web App не загружается
```bash
# Проверка SSL сертификата
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Проверка CORS настроек
curl -H "Origin: https://web.telegram.org" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -X OPTIONS https://your-domain.com/api/auth/telegram/verify
```

### Проблема: Webhook не работает
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

### Проблема: Аутентификация не работает
```javascript
// Отладка аутентификации
console.log('Init Data:', window.Telegram?.WebApp?.initData);
console.log('User:', window.Telegram?.WebApp?.initDataUnsafe?.user);
console.log('Chat:', window.Telegram?.WebApp?.initDataUnsafe?.chat);
```

## 📊 Мониторинг и аналитика

### Метрики бота
```javascript
// Отслеживание событий
function trackEvent(event, data) {
    // Отправка метрик в аналитику
    fetch('/api/analytics/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event, data, platform: 'telegram' })
    });
}

// Отслеживание основных событий
trackEvent('app_opened', { source: 'telegram' });
trackEvent('ride_searched', { from: 'Moscow', to: 'Saint Petersburg' });
trackEvent('ride_booked', { ride_id: 123, price: 1500 });
```

### Логирование
```javascript
// Логирование для отладки
function logTelegramEvent(event, data) {
    console.log(`[Telegram] ${event}:`, data);
    
    // Отправка в серверные логи
    fetch('/api/logs/telegram', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event, data, timestamp: Date.now() })
    });
}
```

## ✅ Чеклист готовности

### Техническая готовность
- [ ] Бот создан через @BotFather
- [ ] Web App настроен
- [ ] SSL сертификат установлен
- [ ] Webhook настроен
- [ ] CORS настроен для web.telegram.org
- [ ] API endpoints работают
- [ ] Аутентификация работает

### Функциональная готовность
- [ ] Поиск поездок работает
- [ ] Бронирование работает
- [ ] Чат работает
- [ ] Платежи работают
- [ ] Уведомления работают
- [ ] Профиль работает

### Безопасность
- [ ] Валидация данных Telegram
- [ ] CSRF защита
- [ ] Санитизация ввода
- [ ] Rate limiting
- [ ] Логирование событий

## 🆘 Поддержка

### Полезные ссылки
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [Telegram Web App Documentation](https://core.telegram.org/bots/webapps)
- [BotFather Commands](https://core.telegram.org/bots#botfather-commands)

### Контакты поддержки
- 📧 **Email**: support@pax-platform.com
- 📱 **Telegram**: @pax_support_bot
- 📚 **Документация**: [docs.pax-platform.com](https://docs.pax-platform.com)

---

**Telegram бот готов к использованию! 🎉**

PAX Platform полностью интегрирована с Telegram и готова для коммерческого использования.