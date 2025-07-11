import { API } from '../api.js';
import Utils from '../utils.js';
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
            continueBtn.addEventListener('click', async () => {
                if (this.isAccepted) {
                    try {
                        // Принимаем пользовательское соглашение
                        const privacyData = {
                            accepted: true,
                            version: "1.1"
                        };
                        
                        // Получаем текущего пользователя (если есть)
                        const currentUser = stateManager.getState('currentUser');
                        if (currentUser) {
                            await API.acceptPrivacyPolicy(currentUser.id, privacyData);
                        }
                        
                        window.router.navigate('basicInfo');
                    } catch (error) {
                        console.error('Ошибка принятия соглашения:', error);
                        // Продолжаем даже если не удалось принять соглашение
                        window.router.navigate('basicInfo');
                    }
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

    async validateAndContinue() {
        try {
            const form = document.getElementById('basicInfoForm');
            if (!form) return;
            
            // Собираем данные формы
            const formData = {
                telegram_id: this.telegramData?.id,
                username: this.telegramData?.username,
                full_name: document.getElementById('fullName').value,
                phone: document.getElementById('phone').value,
                birth_date: document.getElementById('birthDate').value,
                city: document.getElementById('city').value,
                avatar_url: document.getElementById('avatarUrl').value,
                is_driver: false, // Будет установлено на следующем экране
                privacy_policy_accepted: true,
                privacy_policy_version: "1.1"
            };
            
            // Валидация данных
            if (!formData.full_name || formData.full_name.trim().length < 2) {
                Utils.showNotification('Ошибка', 'Введите корректное ФИО', 'error');
                return;
            }
            
            if (!formData.phone || formData.phone.length < 10) {
                Utils.showNotification('Ошибка', 'Введите корректный номер телефона', 'error');
                return;
            }
            
            if (!formData.birth_date) {
                Utils.showNotification('Ошибка', 'Выберите дату рождения', 'error');
                return;
            }
            
            if (!formData.city || formData.city.trim().length < 2) {
                Utils.showNotification('Ошибка', 'Введите город проживания', 'error');
                return;
            }
            
            // Проверяем возраст (18+)
            const birthDate = new Date(formData.birth_date);
            const today = new Date();
            const age = today.getFullYear() - birthDate.getFullYear();
            const monthDiff = today.getMonth() - birthDate.getMonth();
            
            if (age < 18 || (age === 18 && monthDiff < 0)) {
                Utils.showNotification('Ошибка', 'Вам должно быть не менее 18 лет', 'error');
                return;
            }
            
            // Сохраняем данные в состоянии
            stateManager.setState('registrationData', formData);
            
            // Переходим к следующему экрану
            window.router.navigate('driverInfo');
            
        } catch (error) {
            console.error('Ошибка валидации:', error);
            Utils.showNotification('Ошибка', 'Ошибка при валидации данных', 'error');
        }
    }

    async uploadAvatar() {
        try {
            // Создаем input для выбора файла
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            
            input.onchange = async (event) => {
                const file = event.target.files[0];
                if (!file) return;
                
                // Валидация файла
                if (file.size > 5 * 1024 * 1024) { // 5MB
                    Utils.showNotification('Ошибка', 'Размер файла не должен превышать 5MB', 'error');
                    return;
                }
                
                if (!file.type.startsWith('image/')) {
                    Utils.showNotification('Ошибка', 'Выберите изображение', 'error');
                    return;
                }
                
                try {
                    // Создаем FormData для отправки файла
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    // Отправляем файл через API
                    const response = await API.uploadUserAvatar(formData);
                    
                    if (response.success) {
                        // Обновляем превью аватара
                        const avatarPreview = document.getElementById('avatarPreview');
                        const avatarUrl = document.getElementById('avatarUrl');
                        
                        if (avatarPreview) {
                            avatarPreview.innerHTML = `<img src="${response.file_url}" alt="Аватар">`;
                        }
                        
                        if (avatarUrl) {
                            avatarUrl.value = response.file_url;
                        }
                        
                        Utils.showNotification('Успех', 'Аватар успешно загружен', 'success');
                    } else {
                        Utils.showNotification('Ошибка', 'Не удалось загрузить аватар', 'error');
                    }
                } catch (error) {
                    console.error('Ошибка загрузки аватара:', error);
                    Utils.showNotification('Ошибка', 'Не удалось загрузить аватар', 'error');
                }
            };
            
            input.click();
        } catch (error) {
            console.error('Ошибка загрузки аватара:', error);
            Utils.showNotification('Ошибка', 'Ошибка при выборе файла', 'error');
        }
    }

    async getTelegramData() {
        try {
            // Получаем данные из Telegram Web App
            const telegram = window.Telegram?.WebApp;
            if (!telegram) {
                throw new Error('Telegram Web App не доступен');
            }
            
            const userData = telegram.initDataUnsafe?.user || null;
            if (!userData) {
                throw new Error('Данные пользователя Telegram не найдены');
            }
            
            // Верифицируем данные через API
            const verificationData = {
                user: userData,
                auth_date: telegram.initDataUnsafe?.auth_date,
                hash: telegram.initDataUnsafe?.hash,
                initData: telegram.initData
            };
            
            const response = await API.verifyTelegram(verificationData);
            return response.telegram_data || userData;
        } catch (error) {
            console.error('Ошибка получения данных Telegram:', error);
            // Возвращаем базовые данные если верификация не удалась
            const telegram = window.Telegram?.WebApp;
            return telegram?.initDataUnsafe?.user || {};
        }
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

    async completeRegistration() {
        try {
            const form = document.getElementById('driverInfoForm');
            if (!form) return;
            
            // Получаем данные из предыдущего экрана
            const basicData = stateManager.getState('registrationData');
            if (!basicData) {
                Utils.showNotification('Ошибка', 'Данные регистрации не найдены', 'error');
                return;
            }
            
            // Собираем данные водителя
            const hasLicense = document.getElementById('hasLicense').checked;
            const driverData = {
                license_number: document.getElementById('licenseNumber').value,
                car_model: document.getElementById('carModel').value,
                car_year: document.getElementById('carYear').value,
                car_color: document.getElementById('carColor').value,
                car_plate: document.getElementById('carPlate').value
            };
            
            // Объединяем данные
            const registrationData = {
                ...basicData,
                is_driver: hasLicense,
                driver_license_number: hasLicense ? driverData.license_number : null,
                car_brand: hasLicense ? driverData.car_model.split(' ')[0] : null,
                car_model: hasLicense ? driverData.car_model : null,
                car_year: hasLicense ? parseInt(driverData.car_year) : null,
                car_color: hasLicense ? driverData.car_color : null
            };
            
            // Регистрируем пользователя
            const response = await API.registerUser(registrationData);
            
            if (response.success) {
                // Сохраняем данные пользователя в состоянии
                stateManager.setState('currentUser', response.user);
                
                Utils.showNotification('Успех', 'Регистрация завершена успешно!', 'success');
                
                // Переходим к главному экрану
                window.router.navigate('findRide');
            } else {
                Utils.showNotification('Ошибка', 'Не удалось завершить регистрацию', 'error');
            }
            
        } catch (error) {
            console.error('Ошибка завершения регистрации:', error);
            Utils.showNotification('Ошибка', 'Ошибка при завершении регистрации', 'error');
        }
    }
}

// Экспорт всех классов
const RegistrationScreens = {
    privacyPolicy: PrivacyPolicyScreen,
    basicInfo: BasicInfoScreen,
    driverInfo: DriverInfoScreen
};

export default RegistrationScreens;
