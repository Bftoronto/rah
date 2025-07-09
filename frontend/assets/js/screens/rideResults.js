import { stateManager } from '../state.js';

class RideResultsScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render(rides = []) {
        if (!rides || rides.length === 0) {
            return `
                <div class="text-center p-20">
                    <div class="mb-20" style="font-size: 48px; color: #ccc;">
                        <i class="fas fa-car"></i>
                    </div>
                    <h2 class="section-title">Поездки не найдены</h2>
                    <p class="mt-10">Попробуйте изменить параметры поиска</p>
                    <button class="btn btn-outline mt-20" id="changeSearchBtn">Изменить поиск</button>
                </div>
            `;
        }
        
        return `
            <h2 class="section-title">PAX</h2>
            <p class="mb-20">Найдено: ${rides.length} поездок, Сочи - Красная поляна</p>
            
            <h3 class="mb-10">${rides[0].date}</h3>
            
            ${rides.map(ride => `
                <div class="ride-card" data-ride-id="${ride.id}">
                    <div class="ride-time">
                        <span>${ride.time}</span>
                        <span>${ride.duration}</span>
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
                </div>
            `).join('')}
            
            <button class="btn btn-outline" id="loadMoreBtn">Показать еще</button>
        `;
    }

    setupEventHandlers() {
        // Клик по карточке поездки
        document.querySelectorAll('.ride-card').forEach(card => {
            card.addEventListener('click', () => {
                const rideId = card.getAttribute('data-ride-id');
                const ride = this.stateManager.getRides().find(r => r.id === parseInt(rideId));
                if (ride) {
                    this.stateManager.setSelectedRide(ride);
                    window.router.navigate('rideDetails', ride);
                }
            });
        });

        // Изменение поиска
        const changeSearchBtn = document.getElementById('changeSearchBtn');
        if (changeSearchBtn) {
            changeSearchBtn.addEventListener('click', () => {
                window.router.navigate('findRide');
            });
        }

        // Загрузка дополнительных поездок
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => {
                window.router.navigate('loading', 'Загрузка дополнительных поездок...');
                window.api.getRides('Сочи', 'Красная поляна', new Date()).then(additionalRides => {
                    const currentRides = this.stateManager.getRides();
                    const allRides = [...currentRides, ...additionalRides];
                    this.stateManager.setRides(allRides);
                    window.utils.showNotification('Успех', `Загружено еще ${additionalRides.length} поездок`, 'success');
                    window.router.navigate('rideResults', allRides);
                }).catch(error => {
                    window.utils.handleApiError(error, 'loadMoreRides');
                    window.router.navigate('rideResults', this.stateManager.getRides());
                });
            });
        }
    }
}

export default RideResultsScreen; 