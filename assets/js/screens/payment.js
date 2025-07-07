import { stateManager } from '../state.js';

class PaymentMethodScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        return `
            <h2 class="section-title">Выберите способ оплаты</h2>
            
            <div class="card">
                <div class="card-header">Сумма пополнения</div>
                <div class="card-body">
                    <div class="text-center" style="font-size: 24px; font-weight: 500;">${this.stateManager.getState('paymentAmount')} ₽</div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">Способ оплаты</div>
                <div class="card-body">
                    <div class="checkbox">
                        <input type="radio" name="payment" id="sbp" checked>
                        <label for="sbp">СБП</label>
                    </div>
                    <div class="checkbox">
                        <input type="radio" name="payment" id="card">
                        <label for="card">Добавить карту</label>
                    </div>
                </div>
            </div>
            
            <button class="btn btn-primary" id="continuePaymentBtn">Продолжить</button>
        `;
    }

    setupEventHandlers() {
        const continueBtn = document.getElementById('continuePaymentBtn');
        if (continueBtn) {
            continueBtn.addEventListener('click', () => {
                const method = document.querySelector('input[name="payment"]:checked').nextElementSibling.textContent;
                if (method === 'СБП') {
                    window.router.navigate('bankSelection');
                } else {
                    // Для добавления карты
                    alert('Функция добавления карты в разработке');
                }
            });
        }
    }
}

class BankSelectionScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        return `
            <h2 class="section-title">Выбор банка</h2>
            
            <div class="card">
                <div class="list">
                    <div class="list-item">Сбербанк</div>
                    <div class="list-item">T-банк</div>
                    <div class="list-item">Банк ВТБ</div>
                    <div class="list-item">Альфа-банк</div>
                    <div class="list-item">Газпромбанк</div>
                    <div class="list-item">Райффайзенбанк</div>
                    <div class="list-item">Промсвязьбанк</div>
                    <div class="list-item">Совкомбанк</div>
                    <div class="list-item">Россельхозбанк</div>
                </div>
            </div>
            
            <button class="btn btn-outline mt-20" id="backToPaymentBtn">Назад</button>
        `;
    }

    setupEventHandlers() {
        const backBtn = document.getElementById('backToPaymentBtn');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                window.router.navigate('paymentMethod');
            });
        }

        document.querySelectorAll('.list-item').forEach(item => {
            item.addEventListener('click', () => {
                window.router.navigate('loading', 'Обработка платежа...');
                const paymentAmount = this.stateManager.getState('paymentAmount');
                window.api.processPayment(paymentAmount, 'СБП').then(result => {
                    if (result.success) {
                        const userData = this.stateManager.getUserData();
                        userData.balance += paymentAmount;
                        this.stateManager.updateUserData(userData);
                        window.utils.showNotification('Успех', 'Баланс пополнен!', 'success');
                        window.router.navigate('paymentSuccess');
                    }
                }).catch(error => {
                    window.utils.handleApiError(error, 'processPayment');
                    window.router.navigate('bankSelection');
                });
            });
        });
    }
}

class PaymentSuccessScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        return `
            <div class="text-center p-20">
                <div class="mb-20" style="font-size: 48px; color: #4CAF50;">
                    <i class="fas fa-check-circle"></i>
                </div>
                <h2 class="section-title">Оплата прошла успешно</h2>
                <p class="mt-10">Вы забронировали 1 место</p>
                
                <div class="card mt-20">
                    <div class="card-header">11 апреля, пятница</div>
                    <div class="card-body">
                        <div class="mb-10">
                            <strong>Сочи</strong><br>
                            ул. Карла Маркса, д. 2
                        </div>
                        <div>
                            <strong>Эстосадок</strong><br>
                            Остановка Галактика
                        </div>
                    </div>
                </div>
                
                <button class="btn btn-primary mt-20" id="goToRidesBtn">Мои поездки</button>
                
                <div class="driver-info mt-20 justify-center">
                    <div class="driver-avatar">ИИ</div>
                    <div>
                        <div>Иван Иванов</div>
                        <div>123 отзыва</div>
                    </div>
                </div>
                <div class="mt-10">Водитель</div>
            </div>
        `;
    }

    setupEventHandlers() {
        const goToRidesBtn = document.getElementById('goToRidesBtn');
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
    }
}

export default PaymentMethodScreen;
export { BankSelectionScreen, PaymentSuccessScreen }; 