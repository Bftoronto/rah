import { stateManager } from '../state.js';

class CreateRideSuccessScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        return `
            <div class="text-center p-20">
                <div class="mb-20" style="font-size: 48px; color: #4CAF50;">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h2 class="section-title">Поездка создана успешно</h2>
                <p class="mt-10">Ваша поездка добавлена в каталог</p>
                
                <div class="card mt-20">
                    <div class="card-header">Детали поездки</div>
                    <div class="card-body">
                        <div class="mb-10">
                            <strong>Откуда:</strong> ${this.stateManager.getState('newRide').from}
                        </div>
                        <div class="mb-10">
                            <strong>Куда:</strong> ${this.stateManager.getState('newRide').to}
                        </div>
                        <div class="mb-10">
                            <strong>Дата:</strong> ${this.stateManager.getState('newRide').date}
                        </div>
                        <div class="mb-10">
                            <strong>Время:</strong> ${this.stateManager.getState('newRide').time}
                        </div>
                        <div class="mb-10">
                            <strong>Цена:</strong> ${this.stateManager.getState('newRide').price} ₽
                        </div>
                        <div>
                            <strong>Мест:</strong> ${this.stateManager.getState('newRide').passengers}
                        </div>
                    </div>
                </div>
                
                <button class="btn btn-primary mt-20" id="goToMyRidesBtn">Мои поездки</button>
                <button class="btn btn-outline mt-10" id="createAnotherRideBtn">Создать еще одну</button>
            </div>
        `;
    }

    setupEventHandlers() {
        const goToRidesBtn = document.getElementById('goToMyRidesBtn');
        if (goToRidesBtn) {
            goToRidesBtn.addEventListener('click', () => {
                window.router.navigate('loading', 'Загрузка ваших поездок...');
                window.api.getMyRides().then(rides => {
                    window.router.navigate('myRides', rides);
                }).catch(error => {
                    window.utils.handleApiError(error, 'getMyRides');
                    window.router.navigate('myRides');
                });
            });
        }

        const createAnotherBtn = document.getElementById('createAnotherRideBtn');
        if (createAnotherBtn) {
            createAnotherBtn.addEventListener('click', () => {
                window.router.navigate('createRide');
            });
        }
    }
}

export default CreateRideSuccessScreen; 