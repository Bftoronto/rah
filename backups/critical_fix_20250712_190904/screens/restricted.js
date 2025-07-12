import { stateManager } from '../state.js';

class RestrictedScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        return `
            ${this.stateManager.getUserData().balance < 0 ? `
                <div class="warn-banner">
                    <div class="warn-banner-title">Доступ временно ограничен</div>
                    <div class="warn-banner-text">Пожалуйста пополните баланс, чтобы продолжить пользоваться PAX.</div>
                </div>
            ` : ''}
            <div class="access-restricted">
                <div class="access-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h2 class="section-title">Доступ временно ограничен</h2>
                <p>Пожалуйста пополните баланс, чтобы продолжить пользоваться PAX.</p>
                
                <div class="card mt-20">
                    <div class="card-header">PAX</div>
                    <div class="card-body">
                        <ul class="list">
                            <li class="list-item">Поездки с попутчиками</li>
                            <li class="list-item">Пригласить друга</li>
                        </ul>
                    </div>
                </div>
                
                <h3 class="mt-20">Популярные направления</h3>
                <ul class="list mt-10">
                    <li class="list-item">Сочи → Сириус</li>
                    <li class="list-item">Сочи → Красная поляна</li>
                    <li class="list-item">Найти поездку</li>
                </ul>
                
                <button class="btn btn-primary mt-20" id="addBalanceBtn">Пополнить баланс</button>
            </div>
        `;
    }

    setupEventHandlers() {
        const addBalanceBtn = document.getElementById('addBalanceBtn');
        if (addBalanceBtn) {
            addBalanceBtn.addEventListener('click', () => {
                window.router.navigate('paymentMethod');
            });
        }
    }
}

export default RestrictedScreen; 