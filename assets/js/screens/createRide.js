import { stateManager } from '../state.js';

const TOTAL_STEPS = 10;

class CreateRideScreen {
    constructor() {
        this.stateManager = stateManager;
        this.state = this.stateManager.getState('newRide') || {
            passportPhoto: null,
            carPhotos: [],
            from: '',
            to: '',
            stops: [],
            date: '',
            time: '',
            passengers: 1,
            price: 500,
            details: '',
            comfort: true,
        };
        this.currentStep = this.stateManager.getState('createRideStep') || 1;
        this.addStopMode = false;
    }

    render() {
        // Сохраняем шаг в stateManager для возврата
        this.stateManager.setState('createRideStep', this.currentStep);
        switch (this.currentStep) {
            case 1: return this.renderStep1();
            case 2: return this.renderStep2();
            case 3: return this.renderStep3();
            case 4: return this.renderStep4();
            case 5: return this.renderStep5();
            case 6: return this.renderStep6();
            case 7: return this.renderStep7();
            case 8: return this.renderStep8();
            case 9: return this.renderStep9();
            case 10: return this.renderStep10();
            case 11: return this.renderSuccess();
            default: return this.renderStep1();
        }
    }

    // --- INFO BANNER ---
    getInfoBanner() {
        if (window.hideCreateRideInfoBanner) return '';
        return `
            <div class="info-banner" id="createRideInfoBanner">
                <div>
                    <div class="info-banner-title">Внимание</div>
                    <div class="info-banner-text">Перед публикацией убедитесь, что все данные указаны верно.<br>После публикации изменить поездку можно только через отмену.</div>
                </div>
                <button class="info-banner-close" id="closeCreateRideInfoBanner">&times;</button>
            </div>
        `;
    }

    // --- STEP 1 ---
    renderStep1() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <span class="step-title">Шаг 1 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="step-desc step-desc-main">Сделайте селфи с паспортом</div>
                <div class="step-desc step-desc-sub">Никто из пользователей Вашу фотографию не увидит.<br>Этот шаг необходим в целях безопасности.</div>
                <div class="upload-area" id="passportUploadArea" style="margin-top:18px;">
                    ${this.state.passportPhoto ? `<img src="${this.state.passportPhoto}" class="photo-preview" />` : `<div class="upload-icon"><i class="fas fa-plus"></i></div>`}
                    <input type="file" id="passportPhotoInput" accept="image/*" style="display:none;">
                </div>
            </div>
            ${this.renderStepNav(true, !!this.state.passportPhoto)}
        `;
    }

    // --- STEP 2 ---
    renderStep2() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>
                <span class="step-title">Шаг 2 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="step-desc step-desc-main">Загрузите фото автомобиля</div>
                <div class="step-desc step-desc-sub">Это повысит доверие пассажиров</div>
                <div class="upload-area" id="carPhotoUploadArea" style="margin-top:18px;">
                    ${this.state.carPhotos[0] ? `<img src="${this.state.carPhotos[0]}" class="photo-preview" />` : `<div class="upload-icon"><i class="fas fa-plus"></i></div>`}
                    <input type="file" id="carPhotoInput" accept="image/*" style="display:none;">
                </div>
            </div>
            ${this.renderStepNav(true, !!this.state.carPhotos[0])}
        `;
    }

    // --- STEP 3 ---
    renderStep3() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>
                <span class="step-title">Шаг 3 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="step-desc step-desc-main">Укажите, откуда выезжаете</div>
                <div class="step-desc step-desc-sub">Город или адрес</div>
                <div class="form-group">
                    <input type="text" class="form-control" id="fromInput" value="${this.state.from || ''}" placeholder="Город или адрес">
                    <div class="suggestions" id="fromSuggestions"></div>
                </div>
            </div>
            ${this.renderStepNav(true, !!this.state.from)}
        `;
    }

    // --- STEP 4 ---
    renderStep4() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>
                <span class="step-title">Шаг 4 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="step-desc step-desc-main">Куда едете?</div>
                <div class="step-desc step-desc-sub">Город или адрес</div>
                <div class="form-group">
                    <input type="text" class="form-control" id="toInput" value="${this.state.to || ''}" placeholder="Город или адрес">
                    <div class="suggestions" id="toSuggestions"></div>
                </div>
            </div>
            ${this.renderStepNav(true, !!this.state.to)}
        `;
    }

    // --- STEP 5 ---
    renderStep5() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>
                <span class="step-title">Шаг 5 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="route-block">
                    <div class="route-point"><b>${this.state.from || '...'}</b><br><span>${this.state.fromAddress || ''}</span></div>
                    <div class="route-arrow">→</div>
                    <div class="route-point"><b>${this.state.to || '...'}</b><br><span>${this.state.toAddress || ''}</span></div>
                </div>
                <div class="add-stop-block" id="addStopBlock">
                    <div class="add-stop-btn"><i class="fas fa-plus"></i></div>
                    <span>Добавить остановку</span>
                </div>
            </div>
            ${this.renderStepNav(true, true)}
        `;
    }

    // --- STEP 6 ---
    renderStep6() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>
                <span class="step-title">Шаг 6 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="step-desc step-desc-main">Добавьте остановку (необязательно)</div>
                <div class="form-group">
                    <input type="text" class="form-control" id="stopInput" value="${this.state.stops[0] || ''}" placeholder="Город или адрес">
                </div>
            </div>
            ${this.renderStepNav(true, true)}
        `;
    }

    // --- STEP 7 ---
    renderStep7() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>
                <span class="step-title">Шаг 7 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="step-desc step-desc-main">Дата и время поездки</div>
                <div class="step-desc step-desc-sub">Укажите время кратное 5 минутам</div>
                <div class="form-group">
                    <input type="date" class="form-control" id="dateInput" value="${this.state.date || ''}">
                    <input type="time" class="form-control" id="timeInput" value="${this.state.time || ''}" step="300">
                </div>
            </div>
            ${this.renderStepNav(true, !!this.state.date && !!this.state.time && this.isTimeValid(this.state.time))}
        `;
    }

    // --- STEP 8 ---
    renderStep8() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>
                <span class="step-title">Шаг 8 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="passenger-counter">
                    <button class="counter-btn" id="decrementPassengers">-</button>
                    <span class="passenger-value">${this.state.passengers}</span>
                    <button class="counter-btn" id="incrementPassengers">+</button>
                </div>
                <div class="step-desc step-desc-main"><input type="checkbox" id="comfortCheck" ${this.state.comfort ? 'checked' : ''}> Двое на заднем сиденье</div>
                <div class="step-desc step-desc-sub">Это комфорт пассажиров</div>
            </div>
            ${this.renderStepNav(true, this.state.passengers > 0)}
        `;
    }

    // --- STEP 9 ---
    renderStep9() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>
                <span class="step-title">Шаг 9 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="step-desc step-desc-main">Выберите цену за место</div>
                <div class="form-group">
                    <input type="number" class="form-control" id="priceInput" value="${this.state.price}" min="100">
                </div>
            </div>
            ${this.renderStepNav(true, !!this.state.price && this.state.price >= 100)}
        `;
    }

    // --- STEP 10 ---
    renderStep10() {
        return `
            ${this.getInfoBanner()}
            <div class="step-header">
                <button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>
                <span class="step-title">Шаг 10 из 10</span>
            </div>
            <div class="step-content step-center">
                <div class="step-desc step-desc-main">Уточните детали (необязательно)</div>
                <div class="form-group">
                    <textarea class="form-control" id="detailsInput" placeholder="Оставить комментарий к поездке">${this.state.details || ''}</textarea>
                </div>
            </div>
            <button class="btn btn-primary step-final-btn" id="publishBtn">Опубликовать</button>
        `;
    }

    // --- SUCCESS ---
    renderSuccess() {
        return `
            <div class="modal-overlay show" id="successModal">
                <div class="modal">
                    <div class="modal-header">
                        <div class="modal-title"><i class="fas fa-check-circle" style="color: #4CAF50; font-size: 48px;"></i></div>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-20" style="font-size: 22px;">Поездка опубликована!</div>
                        <button class="btn btn-primary" id="successBtn">Отлично!</button>
                    </div>
                </div>
            </div>
        `;
    }

    // --- STEP NAVIGATION ---
    renderStepNav(showBack, nextEnabled) {
        return `
            <div class="step-nav">
                ${showBack && this.currentStep > 1 ? `<button class="step-back" id="stepBackBtn"><i class="fas fa-arrow-left"></i></button>` : '<span></span>'}
            </div>
            <button class="step-next-fab" id="stepNextBtn" ${!nextEnabled ? 'disabled' : ''} title="Далее">
                <i class="fas fa-arrow-right"></i>
            </button>
            <style>
            .container { position: relative; }
            .step-next-fab {
                position: absolute;
                right: 20px;
                bottom: 72px;
                width: 44px;
                height: 44px;
                border-radius: 12px;
                background: #f65446;
                color: #fff;
                font-size: 18px;
                border: none;
                box-shadow: 0 4px 16px rgba(246,84,70,0.18);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 2000;
                transition: background 0.2s, box-shadow 0.2s;
                cursor: pointer;
            }
            .step-next-fab:disabled {
                background: #ffd6cf;
                color: #fff;
                cursor: not-allowed;
                box-shadow: none;
            }
            .step-next-fab i {
                font-size: 20px;
            }
            @media (max-width: 600px) {
                .step-next-fab {
                    position: fixed;
                    right: 12px;
                    bottom: 64px;
                    width: 40px;
                    height: 40px;
                    font-size: 16px;
                    border-radius: 10px;
                }
                .step-next-fab i {
                    font-size: 18px;
                }
            }
            </style>
        `;
    }

    // --- EVENT HANDLERS ---
    setupEventHandlers() {
        // Навигация по шагам
        const nextBtn = document.getElementById('stepNextBtn');
        if (nextBtn) nextBtn.addEventListener('click', () => this.handleNext());
        const backBtn = document.getElementById('stepBackBtn');
        if (backBtn) backBtn.addEventListener('click', () => this.handleBack());
        const publishBtn = document.getElementById('publishBtn');
        if (publishBtn) publishBtn.addEventListener('click', () => this.handlePublish());
        const successBtn = document.getElementById('successBtn');
        if (successBtn) successBtn.addEventListener('click', () => window.router.navigate('findRide'));

        // --- STEP 1: Паспорт ---
        if (this.currentStep === 1) {
            const uploadArea = document.getElementById('passportUploadArea');
            const input = document.getElementById('passportPhotoInput');
            if (uploadArea && input) {
                uploadArea.addEventListener('click', () => input.click());
                input.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (file && file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (ev) => {
                            this.state.passportPhoto = ev.target.result;
                            this.saveAndRerender();
                        };
                        reader.readAsDataURL(file);
                    }
                });
            }
        }
        // --- STEP 2: Фото авто ---
        if (this.currentStep === 2) {
            document.querySelectorAll('.upload-slot').forEach(slot => {
                const idx = +slot.getAttribute('data-index');
                const input = slot.querySelector('input[type="file"]');
                slot.addEventListener('click', () => input.click());
                input.addEventListener('change', (e) => {
                    const file = e.target.files[0];
                    if (file && file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = (ev) => {
                            this.state.carPhotos[idx] = ev.target.result;
                            this.saveAndRerender();
                        };
                        reader.readAsDataURL(file);
                    }
                });
            });
        }
        // --- STEP 3: Откуда ---
        if (this.currentStep === 3) {
            const fromInput = document.getElementById('fromInput');
            if (fromInput) {
                fromInput.addEventListener('input', (e) => {
                    this.state.from = e.target.value;
                    this.saveAndRerender(false);
                    // Автодополнение (заглушка)
                    const suggestions = ['Калининград','Киров','Кисловодск','Краснодар','Красноярск'];
                    this.showSuggestions('fromSuggestions', suggestions, e.target.value, (val) => {
                        this.state.from = val;
                        this.saveAndRerender();
                    });
                });
            }
        }
        // --- STEP 4: Куда ---
        if (this.currentStep === 4) {
            const toInput = document.getElementById('toInput');
            if (toInput) {
                toInput.addEventListener('input', (e) => {
                    this.state.to = e.target.value;
                    this.saveAndRerender(false);
                    // Автодополнение (заглушка)
                    const suggestions = ['Сочи, ул. Ленина','Сочи, ул. Ленина, д. 1','Сочи, ул. Ленина, д. 15','Сочи, ул. Ленина, д. 2','Сочи, ул. Ленина, д. 39','Сочи, ул. Ленина, д. 55'];
                    this.showSuggestions('toSuggestions', suggestions, e.target.value, (val) => {
                        this.state.to = val;
                        this.saveAndRerender();
                    });
                });
            }
        }
        // --- STEP 5: Добавить остановку ---
        if (this.currentStep === 5) {
            const addStopBlock = document.getElementById('addStopBlock');
            if (addStopBlock) {
                addStopBlock.addEventListener('click', () => {
                    this.currentStep = 6;
                    this.saveAndRerender();
                });
            }
        }
        // --- STEP 6: Остановка ---
        if (this.currentStep === 6) {
            const stopInput = document.getElementById('stopInput');
            if (stopInput) {
                stopInput.addEventListener('input', (e) => {
                    this.state.stops[0] = e.target.value;
                    this.saveAndRerender(false);
                });
            }
        }
        // --- STEP 7: Дата и время ---
        if (this.currentStep === 7) {
            const dateInput = document.getElementById('dateInput');
            const timeInput = document.getElementById('timeInput');
            if (dateInput) dateInput.addEventListener('change', (e) => { this.state.date = e.target.value; this.saveAndRerender(); });
            if (timeInput) timeInput.addEventListener('change', (e) => { this.state.time = e.target.value; this.saveAndRerender(); });
        }
        // --- STEP 8: Пассажиры ---
        if (this.currentStep === 8) {
            const decBtn = document.getElementById('decrementPassengers');
            const incBtn = document.getElementById('incrementPassengers');
            const comfortCheck = document.getElementById('comfortCheck');
            if (decBtn) decBtn.addEventListener('click', () => { if (this.state.passengers > 1) { this.state.passengers--; this.saveAndRerender(); } });
            if (incBtn) incBtn.addEventListener('click', () => { this.state.passengers++; this.saveAndRerender(); });
            if (comfortCheck) comfortCheck.addEventListener('change', (e) => { this.state.comfort = e.target.checked; this.saveAndRerender(false); });
        }
        // --- STEP 9: Цена ---
        if (this.currentStep === 9) {
            const priceInput = document.getElementById('priceInput');
            if (priceInput) priceInput.addEventListener('input', (e) => { this.state.price = +e.target.value; this.saveAndRerender(false); });
        }
        // --- STEP 10: Детали ---
        if (this.currentStep === 10) {
            const detailsInput = document.getElementById('detailsInput');
            if (detailsInput) detailsInput.addEventListener('input', (e) => { this.state.details = e.target.value; this.saveAndRerender(false); });
        }
        // Закрытие info-banner
        const closeBanner = document.getElementById('closeCreateRideInfoBanner');
        if (closeBanner) {
            closeBanner.addEventListener('click', () => {
                window.hideCreateRideInfoBanner = true;
                document.getElementById('createRideInfoBanner').style.display = 'none';
            });
        }
    }

    showSuggestions(containerId, suggestions, value, onSelect) {
        const container = document.getElementById(containerId);
        if (!container) return;
        container.innerHTML = '';
        if (!value) return;
        const filtered = suggestions.filter(s => s.toLowerCase().startsWith(value.toLowerCase()));
        filtered.forEach(s => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = s;
            div.addEventListener('click', () => onSelect(s));
            container.appendChild(div);
        });
    }

    saveAndRerender(rerender = true) {
        this.stateManager.setState('newRide', this.state);
        if (rerender !== false) window.router.navigate('createRide');
    }

    handleNext() {
        if (this.currentStep < TOTAL_STEPS) {
            this.currentStep++;
            this.saveAndRerender();
        }
    }
    handleBack() {
        if (this.currentStep > 1) {
            this.currentStep--;
            this.saveAndRerender();
        }
    }
    handlePublish() {
        this.currentStep = 11;
        this.saveAndRerender();
    }
    isTimeValid(time) {
        if (!time) return false;
        const [h, m] = time.split(':').map(Number);
        return m % 5 === 0;
    }
}

export default CreateRideScreen;
