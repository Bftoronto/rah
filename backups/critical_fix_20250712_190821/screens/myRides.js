import { stateManager } from '../state.js';

class MyRidesScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render(rides = []) {
        return `
            ${!this.stateManager.getState('hideMyRidesInfoBanner') ? `
                <div class="info-banner" id="myRidesInfoBanner">
                    <div>
                        <div class="info-banner-title">Отмена поездки</div>
                        <div class="info-banner-text">Вы можете отменить поездку в течение 15 минут без понижения рейтинга</div>
                    </div>
                    <button class="info-banner-close" id="closeMyRidesInfoBanner">&times;</button>
                </div>
            ` : ''}
            <!-- <h2 class="section-title">Ваши поездки</h2> -->
            
            ${rides.length === 0 ? `
                <div class="text-center p-20">
                    <div class="mb-20" style="font-size: 48px; color: #ccc;">
                        <i class="fas fa-car"></i>
                    </div>
                    <p>У вас пока нет активных поездок</p>
                    <button class="btn btn-primary mt-20" id="createRideBtn">Создать поездку</button>
                </div>
            ` : `
                ${rides.map(ride => {
                    // Определяем, прошла ли поездка
                    const now = new Date();
                    const [day, monthName] = ride.date.split(' ');
                    const months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'];
                    const month = months.indexOf(monthName);
                    let rideDateTime = new Date(now.getFullYear(), month, parseInt(day));
                    if (ride.time) {
                        const [h, m] = ride.time.split(':');
                        rideDateTime.setHours(parseInt(h), parseInt(m), 0, 0);
                    }
                    const isFuture = rideDateTime.getTime() > now.getTime();
                    return `
                    <div class="ride-card" data-ride-id="${ride.id}">
                        <div class="card-header">${ride.date}</div>
                        <div class="ride-time">
                            <span>${ride.time}</span>
                        </div>
                        
                        <div class="ride-location">
                            <div class="ride-location-dot start"></div>
                            <div class="ride-location-text">
                                <div class="location-title">${ride.from.split(',')[0]}</div>
                                <div>${ride.from.split(',').slice(1).join(',').trim()}</div>
                            </div>
                            
                            <div class="ride-location-dot end"></div>
                            <div class="ride-location-text">
                                <div class="location-title">${ride.to.split(',')[0]}</div>
                                <div>${ride.to.split(',').slice(1).join(',').trim()}</div>
                            </div>
                        </div>
                        
                        <div class="ride-footer">
                            <div class="driver-info">
                                <div class="driver-avatar">${ride.driver.name.split(' ').map(n => n[0]).join('')}</div>
                                <div>${ride.driver.name}</div>
                            </div>
                            <div class="ride-price">${ride.price} ₽</div>
                        </div>
                        <div class="ride-payment-info" aria-label="Способы оплаты" style="margin-top:4px;font-size:14px;">
                            <span role="img" aria-label="наличные">💵</span> Наличный расчет <span style="color:#bbb;">|</span> <span role="img" aria-label="перевод на карту">💳</span> Перевод на карту
                        </div>
                        
                        ${ride.passengers.length > 0 ? `
                            <div class="card-body">
                                <div class="form-label">Ваши пассажиры</div>
                                <div>${ride.passengers.join(', ')}</div>
                            </div>
                        ` : ''}
                        
                        ${isFuture ? `<div class="card-body">
                            <button class="btn btn-outline w-100" data-action="cancel" data-ride-id="${ride.id}">
                                ${ride.status === 'booked' ? 'Отменить бронирование' : 'Отменить поездку'}
                            </button>
                        </div>` : ''}
                    </div>
                    `;
                }).join('')}
            `}
        `;
    }

    setupEventHandlers() {
        // Закрытие информационного баннера
        const closeBanner = document.getElementById('closeMyRidesInfoBanner');
        if (closeBanner) {
            closeBanner.addEventListener('click', () => {
                this.stateManager.setState('hideMyRidesInfoBanner', true);
                window.router.navigate('myRides');
            });
        }

        // Кнопка создания поездки
        const createRideBtn = document.getElementById('createRideBtn');
        if (createRideBtn) {
            createRideBtn.addEventListener('click', () => {
                window.router.navigate('createRide');
            });
        }

        // Обработчики отмены поездок
        document.querySelectorAll('[data-action="cancel"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const rideId = btn.getAttribute('data-ride-id');
                const ride = this.stateManager.getRides().find(r => r.id === parseInt(rideId));
                
                if (confirm(`Вы уверены, что хотите отменить поездку${ride ? ` "${ride.from} → ${ride.to}"` : ''}?`)) {
                    window.router.navigate('loading', 'Отмена поездки...');
                    
                    setTimeout(() => {
                        const userData = this.stateManager.getUserData();
                        userData.cancelledRides = (userData.cancelledRides || 0) + 1;
                        this.stateManager.updateUserData(userData);
                        window.utils.showNotification('Успех', 'Поездка успешно отменена', 'success');
                        
                        window.api.getMyRides().then(rides => {
                            window.router.navigate('myRides', rides);
                        }).catch(error => {
                            window.utils.handleApiError(error, 'getMyRides');
                            window.router.navigate('myRides');
                        });
                    }, 1500);
                }
            });
        });
    }
}

export default MyRidesScreen; 