import { stateManager } from '../state.js';

class DriverProfileScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render(driver) {
        const selectedDriver = driver || this.stateManager.getSelectedRide()?.driver;
        if (!selectedDriver) {
            return '<div class="text-center p-20">Информация о водителе не найдена</div>';
        }

        return `
            <div class="profile-header">
                <div class="profile-name">${selectedDriver.name}</div>
                <div class="rating">
                    <div class="stars">★★★★★</div>
                    <div class="rating-value">${selectedDriver.rating}</div>
                </div>
                <div>${selectedDriver.reviews} отзыва</div>
            </div>
            
            <div class="d-flex justify-between p-20">
                <div class="text-center">
                    <div class="stars">★★★★★</div>
                    <div>100%</div>
                    <div>${selectedDriver.reviews} отзывов</div>
                </div>
                
                <div class="text-center">
                    <div class="stars">★★★★☆</div>
                    <div>0%</div>
                    <div>0 отзывов</div>
                </div>
                
                <div class="text-center">
                    <div class="stars">★★★☆☆</div>
                    <div>0%</div>
                    <div>0 отзывов</div>
                </div>
                
                <div class="text-center">
                    <div class="stars">★☆☆☆☆</div>
                    <div>0%</div>
                    <div>0 отзывов</div>
                </div>
            </div>
            
            <div class="card">
                <div class="list">
                    <div class="review">
                        <div class="review-header">
                            <div class="review-name">Соня</div>
                            <div class="review-date">10.04.2025 в 9:41</div>
                        </div>
                        <div class="stars">★★★★★</div>
                        <div class="mt-10">Отличный водитель, все понравилось!</div>
                    </div>
                    
                    <div class="review">
                        <div class="review-header">
                            <div class="review-name">Семен</div>
                            <div class="review-date">10.04.2025 в 9:41</div>
                        </div>
                        <div class="stars">★★★★★</div>
                        <div class="mt-10">Чистый автомобиль, пунктуальный водитель.</div>
                    </div>
                    
                    <div class="review">
                        <div class="review-header">
                            <div class="review-name">Роман</div>
                            <div class="review-date">10.04.2025 в 9:41</div>
                        </div>
                        <div class="stars">★★★★★</div>
                        <div class="mt-10">Удобная поездка, рекомендую!</div>
                    </div>
                </div>
            </div>
            
            <button class="btn btn-primary mt-20" id="bookRideBtn">Забронировать поездку</button>
            <button class="btn btn-outline mt-10" id="openChatBtn">
                <i class="fas fa-comments"></i> Написать водителю
            </button>
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
                        window.router.navigate('driverProfile', selectedRide.driver);
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
                    window.router.navigate('driverProfile', selectedRide.driver);
                });
            });
        }
    }
}

export default DriverProfileScreen; 