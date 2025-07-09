import { API } from '../api.js';
import { Utils } from '../utils.js';
import { stateManager } from '../state.js';

// Экран пользовательского соглашения
class PrivacyPolicyScreen {
    constructor() {
        this.policyContent = null;
        this.isAccepted = false;
    }

    async render() {
        try {
            // Загружаем текст соглашения
            if (!this.policyContent) {
                const response = await API.getPrivacyPolicy();
                this.policyContent = response.content;
            }

            return `
                <div class="registration-container">
                    <div class="registration-header">
                        <h1 class="section-title">Пользовательское соглашение</h1>
                        <p class="text-muted">Версия 1.1</p>
                    </div>
                    
                    <div class="policy-content">
                        <div class="policy-text">
                            ${this.policyContent}
                        </div>
                    </div>
                    
                    <div class="policy-acceptance">
                        <label class="checkbox-container">
                            <input type="checkbox" id="policyAccepted" ${this.isAccepted ? 'checked' : ''}>
                            <span class="checkmark"></span>
                            <span class="checkbox-text">
                                Я принимаю <a href="#" id="downloadPolicy">Правила конфиденциальности</a> 
                                и пользовательское соглашение
                            </span>
                        </label>
                    </div>
                    
                    <div class="registration-actions">
                        <button class="btn btn-primary btn-full" id="continueToBasic" ${!this.isAccepted ? 'disabled' : ''}>
                            Продолжить
                        </button>
                    </div>
                </div>
            `;
        } catch (error) {
            console.error('Ошибка загрузки соглашения:', error);
            return `
                <div class="error-container">
                    <div class="error-icon">⚠️</div>
                    <h2>Ошибка загрузки</h2>
                    <p>Не удалось загрузить пользовательское соглашение</p>
                    <button class="btn btn-primary" onclick="location.reload()">Попробовать снова</button>
                </div>
            `;
        }
    }

    setupEventHandlers() {
        const policyCheckbox = document.getElementById('policyAccepted');
        const continueBtn = document.getElementById('continueToBasic');
        const downloadLink = document.getElementById('downloadPolicy');

        if (policyCheckbox) {
            policyCheckbox.addEventListener('change', (e) => {
                this.isAccepted = e.target.checked;
                continueBtn.disabled = !this.isAccepted;
            });
        }

        if (continueBtn) {
            continueBtn.addEventListener('click', () => {
                if (this.isAccepted) {
                    window.router.navigate('basicInfo');
                }
            });
        }

        if (downloadLink) {
            downloadLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.downloadPolicyFile();
            });
        }
    }

    async downloadPolicyFile() {
        try {
            // Создаем ссылку для скачивания файла
            const link = document.createElement('a');
            link.href = './Правила конфидециальности.docx';
            link.download = 'Правила конфидециальности.docx';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error('Ошибка скачивания файла:', error);
            Utils.showNotification('Ошибка', 'Не удалось скачать файл', 'error');
        }
    }
}

// Экран базовой информации
class BasicInfoScreen {
    constructor() {
        this.telegramData = null;
        this.formData = {
            phone: '',
            fullName: '',
            birthDate: '',
            city: '',
            avatarUrl: ''
        };
    }

    async render() {
        // Получаем данные Telegram
        if (!this.telegramData) {
            this.telegramData = await this.getTelegramData();
        }

        return `
            <div class="registration-container">
                <div class="registration-header">
                    <h1 class="section-title">Основная информация</h1>
                    <p class="text-muted">Заполните основные данные профиля</p>
                </div>
                
                <form id="basicInfoForm" class="registration-form">
                    <div class="form-group">
                        <label for="telegramId">Telegram ID</label>
                        <input type="text" id="telegramId" value="${this.telegramData?.id || ''}" readonly>
                        <small class="form-text">Автоматически заполняется из Telegram</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="phone">Номер телефона *</label>
                        <input type="tel" id="phone" required placeholder="+7 (999) 123-45-67">
                        <small class="form-text">Будет использоваться для связи</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="fullName">ФИО *</label>
                        <input type="text" id="fullName" required placeholder="Иванов Иван Иванович">
                        <small class="form-text">Ваше полное имя</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="birthDate">Дата рождения *</label>
                        <input type="date" id="birthDate" required>
                        <small class="form-text">Вам должно быть не менее 18 лет</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="city">Город проживания *</label>
                        <input type="text" id="city" required placeholder="Москва">
                        <small class="form-text">Город, где вы проживаете</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="avatarUrl">Аватар профиля</label>
                        <div class="avatar-upload">
                            <div class="avatar-preview" id="avatarPreview">
                                <img src="${this.telegramData?.photo_url || '/assets/images/default-avatar.png'}" alt="Аватар">
                            </div>
                            <button type="button" class="btn btn-secondary" id="uploadAvatar">
                                Загрузить фото
                            </button>
                        </div>
                        <input type="hidden" id="avatarUrl" value="${this.telegramData?.photo_url || ''}">
                    </div>
                </form>
                
                <div class="registration-actions">
                    <button class="btn btn-secondary" id="backToPolicy">Назад</button>
                    <button class="btn btn-primary" id="continueToDriver">Продолжить</button>
                </div>
            </div>
        `;
    }

    setupEventHandlers() {
        const form = document.getElementById('basicInfoForm');
        const backBtn = document.getElementById('backToPolicy');
        const continueBtn = document.getElementById('continueToDriver');
        const uploadBtn = document.getElementById('uploadAvatar');

        if (backBtn) {
            backBtn.addEventListener('click', () => {
                window.router.navigate('privacyPolicy');
            });
        }

        if (continueBtn) {
            continueBtn.addEventListener('click', () => {
                this.validateAndContinue();
            });
        }

        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => {
                this.uploadAvatar();
            });
        }
    }

    validateAndContinue() {
        // Логика валидации и продолжения
        console.log('Валидация и продолжение');
        window.router.navigate('driverInfo');
    }

    async uploadAvatar() {
        // Логика загрузки аватара
        console.log('Загрузка аватара');
    }

    async getTelegramData() {
        // Получение данных из Telegram
        if (window.Telegram && window.Telegram.WebApp) {
            return window.Telegram.WebApp.initDataUnsafe?.user || {};
        }
        return {};
    }
}

// Экран информации о водителе
class DriverInfoScreen {
    constructor() {
        this.formData = {
            hasLicense: false,
            licenseNumber: '',
            carModel: '',
            carYear: '',
            carColor: '',
            carPlate: ''
        };
    }

    render() {
        return `
            <div class="registration-container">
                <div class="registration-header">
                    <h1 class="section-title">Информация о водителе</h1>
                    <p class="text-muted">Заполните данные о водительском удостоверении и автомобиле</p>
                </div>
                
                <form id="driverInfoForm" class="registration-form">
                    <div class="form-group">
                        <label class="checkbox-container">
                            <input type="checkbox" id="hasLicense" ${this.formData.hasLicense ? 'checked' : ''}>
                            <span class="checkmark"></span>
                            <span class="checkbox-text">У меня есть водительское удостоверение</span>
                        </label>
                    </div>
                    
                    <div id="licenseInfo" class="${this.formData.hasLicense ? '' : 'hidden'}">
                        <div class="form-group">
                            <label for="licenseNumber">Номер водительского удостоверения</label>
                            <input type="text" id="licenseNumber" placeholder="0000 000000" value="${this.formData.licenseNumber}">
                        </div>
                        
                        <div class="form-group">
                            <label for="carModel">Марка и модель автомобиля</label>
                            <input type="text" id="carModel" placeholder="Toyota Camry" value="${this.formData.carModel}">
                        </div>
                        
                        <div class="form-group">
                            <label for="carYear">Год выпуска</label>
                            <input type="number" id="carYear" placeholder="2020" value="${this.formData.carYear}">
                        </div>
                        
                        <div class="form-group">
                            <label for="carColor">Цвет автомобиля</label>
                            <input type="text" id="carColor" placeholder="Белый" value="${this.formData.carColor}">
                        </div>
                        
                        <div class="form-group">
                            <label for="carPlate">Государственный номер</label>
                            <input type="text" id="carPlate" placeholder="A 123 BC 77" value="${this.formData.carPlate}">
                        </div>
                    </div>
                </form>
                
                <div class="registration-actions">
                    <button class="btn btn-secondary" id="backToBasic">Назад</button>
                    <button class="btn btn-primary" id="completeRegistration">Завершить регистрацию</button>
                </div>
            </div>
        `;
    }

    setupEventHandlers() {
        const hasLicenseCheckbox = document.getElementById('hasLicense');
        const licenseInfo = document.getElementById('licenseInfo');
        const backBtn = document.getElementById('backToBasic');
        const completeBtn = document.getElementById('completeRegistration');

        if (hasLicenseCheckbox) {
            hasLicenseCheckbox.addEventListener('change', (e) => {
                this.formData.hasLicense = e.target.checked;
                if (licenseInfo) {
                    licenseInfo.classList.toggle('hidden', !e.target.checked);
                }
            });
        }

        if (backBtn) {
            backBtn.addEventListener('click', () => {
                window.router.navigate('basicInfo');
            });
        }

        if (completeBtn) {
            completeBtn.addEventListener('click', () => {
                this.completeRegistration();
            });
        }
    }

    completeRegistration() {
        // Логика завершения регистрации
        console.log('Завершение регистрации');
        window.router.navigate('findRide');
    }
}

// Экспорт всех классов
const RegistrationScreens = {
    privacyPolicy: PrivacyPolicyScreen,
    basicInfo: BasicInfoScreen,
    driverInfo: DriverInfoScreen
};

export default RegistrationScreens;
