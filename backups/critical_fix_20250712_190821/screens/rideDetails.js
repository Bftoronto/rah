import { stateManager } from '../state.js';

class RideDetailsScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render(ride) {
        const selectedRide = ride || this.stateManager.getSelectedRide();
        if (!selectedRide) {
            return '<div class="text-center p-20">Поездка не найдена</div>';
        }

        return `
            <div class="ride-card">
                <div class="ride-time">
                    <span>${selectedRide.time}</span>
                    <span>${selectedRide.duration}</span>
                </div>
                
                <div class="ride-location">
                    <div class="ride-location-dot start"></div>
                    <div class="ride-location-text">
                        <div class="location-title">${selectedRide.from.split(',')[0]}</div>
                        <div>${selectedRide.from.split(',').slice(1).join(',').trim()}</div>
                    </div>
                    
                    <div class="ride-location-dot end"></div>
                    <div class="ride-location-text">
                        <div class="location-title">${selectedRide.to.split(',')[0]}</div>
                        <div>${selectedRide.to.split(',').slice(1).join(',').trim()}</div>
                    </div>
                </div>
                
                <div class="ride-footer">
                    <div class="driver-info">
                        <div class="driver-avatar">${selectedRide.driver.name.split(' ').map(n => n[0]).join('')}</div>
                        <div>
                            <div>${selectedRide.driver.name}</div>
                            <div class="rating">
                                <div class="stars">★★★★★</div>
                                <div class="rating-value">${selectedRide.driver.rating}</div>
                                <div>(${selectedRide.driver.reviews} отзывов)</div>
                            </div>
                        </div>
                    </div>
                    <div class="ride-price">${selectedRide.price} ₽</div>
                </div>
                <div class="ride-payment-info" aria-label="Способы оплаты" style="margin-top:8px;font-size:15px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <span role="img" aria-label="наличные">💵</span> Наличный расчет <span style="color:#bbb;">|</span> <span role="img" aria-label="перевод на карту">💳</span> Перевод на карту
                </div>
            </div>
            
            <div class="card mt-20">
                <div class="card-header">Информация о водителе</div>
                <div class="card-body">
                    <div class="d-flex justify-between align-center mb-10">
                        <span>Автомобиль</span>
                        <span>LADA Granta, 2023</span>
                    </div>
                    <div class="d-flex justify-between align-center mb-10">
                        <span>Цвет</span>
                        <span>Серый</span>
                    </div>
                    <div class="d-flex justify-between align-center mb-10">
                        <span>Номер</span>
                        <span>A 123 AA</span>
                    </div>
                    <div class="d-flex justify-between align-center">
                        <span>Свободных мест</span>
                        <span>3</span>
                    </div>
                </div>
            </div>
            
            <div class="card mt-20">
                <div class="card-header">Правила поездки</div>
                <div class="card-body">
                    <ul style="padding-left: 20px;">
                        <li>Курение запрещено</li>
                        <li>Можно с животными</li>
                        <li>Можно с детьми</li>
                        <li>Багаж включен в стоимость</li>
                    </ul>
                </div>
            </div>
            
            <button class="btn btn-primary mt-20" id="bookRideBtn">Забронировать место</button>
            <button class="btn btn-outline mt-10" id="openChatBtn">
                <i class="fas fa-comments"></i> Написать водителю
            </button>
            <div class="ride-payment-info" aria-label="Способы оплаты" style="margin-top:16px;font-size:15px;text-align:center;">
                <span role="img" aria-label="наличные">💵</span> Наличный расчет <span style="color:#bbb;">|</span> <span role="img" aria-label="перевод на карту">💳</span> Перевод на карту<br>
                <span style="font-size:13px;color:#888;">Все расчеты осуществляются напрямую между пассажиром и водителем</span>
            </div>
        `;
    }

    setupEventHandlers() {
        // Бронирование поездки
        const bookRideBtn = document.getElementById('bookRideBtn');
        if (bookRideBtn) {
            bookRideBtn.addEventListener('click', () => {
                const selectedRide = this.stateManager.getSelectedRide();
                const userData = this.stateManager.getUserData();
                if (userData.balance < selectedRide.price) {
                    window.router.navigate('paymentMethod');
                } else {
                    window.router.navigate('loading', 'Бронирование поездки...');
                    window.api.bookRide(selectedRide.id).then(result => {
                        if (result.success) {
                            userData.balance -= selectedRide.price;
                            this.stateManager.updateUserData(userData);
                            window.utils.showNotification('Успех', 'Поездка забронирована!', 'success');
                            window.router.navigate('paymentSuccess');
                        }
                    }).catch(error => {
                        window.utils.handleApiError(error, 'bookRide');
                        window.router.navigate('rideDetails', selectedRide);
                    });
                }
            });
        }

        // Открытие чата с водителем
        const openChatBtn = document.getElementById('openChatBtn');
        if (openChatBtn) {
            openChatBtn.addEventListener('click', () => {
                // Загружаем сообщения чата
                const selectedRide = this.stateManager.getSelectedRide();
                const chatId = `chat_${selectedRide.id}`;
                this.stateManager.setState('chat', { ...this.stateManager.getState('chat'), currentChatId: chatId });
                window.router.navigate('loading', 'Загрузка чата...');
                
                window.api.getChatMessages(chatId).then(messages => {
                    this.stateManager.setChatMessages(messages);
                    window.router.navigate('chatScreen');
                }).catch(error => {
                    window.utils.handleApiError(error, 'loadChat');
                    window.router.navigate('rideDetails', selectedRide);
                });
            });
        }
    }
}

export default RideDetailsScreen; 