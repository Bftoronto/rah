import { stateManager } from '../state.js';
import { API } from '../api.js';
import Utils from '../utils.js';

// Экран поиска поездок
class FindRideScreen {
    constructor() {}
    
    // Получение HTML шаблона
    getTemplate() {
        const userData = stateManager.getUserData();
        const selectedDate = stateManager.getSelectedDate();
        
        return `
            ${userData.cancelledRides >= 3 ? `
                <div class="block-banner">
                    <div class="block-banner-title">Аккаунт заблокирован</div>
                    <div class="block-banner-text">Вы превысили количество отменных поездок</div>
                </div>
            ` : ''}
            
            <div class="form-group">
                <label class="form-label">Откуда</label>
                <input type="text" class="form-control" id="fromInput" placeholder="Введите место отправления">
            </div>
            
            <div class="form-group">
                <label class="form-label">Куда</label>
                <input type="text" class="form-control" id="toInput" placeholder="Введите место назначения">
            </div>
            
            <div class="form-group">
                <label class="form-label">Дата</label>
                <input type="text" class="form-control" id="dateInput" value="${selectedDate ? Utils.formatDisplayDate(selectedDate) : 'Сегодня'}" readonly>
            </div>
            
            <div class="form-group">
                <label class="form-label">Количество мест</label>
                <div class="d-flex align-center">
                    <button class="btn btn-secondary btn-small" id="decrementSeats">-</button>
                    <input type="text" class="form-control" id="seatsInput" value="1" style="text-align: center; margin: 0 8px;" readonly>
                    <button class="btn btn-secondary btn-small" id="incrementSeats">+</button>
                </div>
            </div>
            
            <div class="find-btn-fixed-wrap">
                <button class="btn btn-primary find-btn-fixed" id="findRideBtn">Найти</button>
            </div>
            
            <style>
            .find-btn-fixed-wrap {
                position: fixed;
                left: 0;
                right: 0;
                bottom: 72px;
                width: 100vw;
                display: flex;
                justify-content: center;
                z-index: 1500;
                pointer-events: none;
            }
            .find-btn-fixed {
                width: calc(100vw - 32px);
                max-width: 432px;
                margin: 0 auto;
                border-radius: 16px;
                font-size: 17px;
                padding: 14px 0;
                pointer-events: all;
            }
            @media (max-width: 600px) {
                .find-btn-fixed-wrap {
                    bottom: 64px;
                }
                .find-btn-fixed {
                    width: 92vw;
                    max-width: 432px;
                    font-size: 16px;
                    padding: 12px 0;
                    border-radius: 14px;
                }
            }
            </style>
        `;
    }
    
    render(data = null) {
        return this.getTemplate();
    }
    
    setupEventHandlers() {
        // Обработчик кнопки поиска
        const findBtn = document.getElementById('findRideBtn');
        if (findBtn) {
            findBtn.addEventListener('click', this.handleSearch.bind(this));
        }
        
        // Обработчик выбора даты
        const dateInput = document.getElementById('dateInput');
        if (dateInput) {
            dateInput.addEventListener('click', () => {
                window.router.navigate('dateSelection');
            });
        }
        
        // Обработчики количества мест
        const incrementSeats = document.getElementById('incrementSeats');
        const decrementSeats = document.getElementById('decrementSeats');
        
        if (incrementSeats) {
            incrementSeats.addEventListener('click', () => {
                const seatsInput = document.getElementById('seatsInput');
                if (seatsInput) {
                    seatsInput.value = parseInt(seatsInput.value) + 1;
                }
            });
        }
        
        if (decrementSeats) {
            decrementSeats.addEventListener('click', () => {
                const seatsInput = document.getElementById('seatsInput');
                if (seatsInput) {
                    const value = parseInt(seatsInput.value);
                    if (value > 1) {
                        seatsInput.value = value - 1;
                    }
                }
            });
        }
        
        // Валидация в реальном времени
        this.setupValidation();
        
        // Блокировка поиска, если превышен лимит отмен
        const userData = stateManager.getUserData();
        if (userData.cancelledRides >= 3 && findBtn) {
            findBtn.disabled = true;
            findBtn.style.opacity = 0.6;
            findBtn.style.cursor = 'not-allowed';
        }
    }
    
    // Настройка валидации
    setupValidation() {
        ['fromInput', 'toInput'].forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('blur', () => {
                    const value = field.value;
                    const rules = { required: true, minLength: 2 };
                    const errors = Utils.validateField(value, rules);
                    
                    if (errors.length > 0) {
                        Utils.showFieldError(field, errors[0]);
                    } else {
                        Utils.hideFieldError(field);
                    }
                });
                
                field.addEventListener('input', () => {
                    Utils.hideFieldError(field);
                });
            }
        });
    }
    
    // Обработка поиска
    async handleSearch() {
        Utils.clearFormErrors();
        
        const formData = this.getFormData();
        const validation = Utils.validateForm(formData, {
            fromInput: { required: true, minLength: 2 },
            toInput: { required: true, minLength: 2 }
        });
        
        if (!validation.isValid) {
            Utils.showFormErrors(validation.errors);
            Utils.showNotification('Ошибка', 'Пожалуйста, исправьте ошибки в форме', 'error');
            return;
        }
        
        try {
            // Показываем экран загрузки
            await window.router.navigate('loading', 'Поиск поездок...');
            
            // Выполняем поиск
            const rides = await API.getRides(formData.fromInput, formData.toInput, new Date());
            
            // Сохраняем результаты в состояние
            stateManager.setRides(rides);
            
            // Переходим к результатам
            await window.router.navigate('rideResults', rides);
            
            Utils.showNotification('Поиск завершен', `Найдено ${rides.length} поездок`, 'success');
        } catch (error) {
            Utils.handleApiError(error, 'searchRides');
            await window.router.navigate('findRide');
        }
    }
    
    // Получение данных формы
    getFormData() {
        return {
            fromInput: document.getElementById('fromInput')?.value || '',
            toInput: document.getElementById('toInput')?.value || '',
            dateInput: stateManager.getSelectedDate(),
            seatsInput: document.getElementById('seatsInput')?.value || '1'
        };
    }
    
    // Очистка экрана
    destroy() {
        // Удаляем обработчики событий при необходимости
    }
}

export default FindRideScreen; 