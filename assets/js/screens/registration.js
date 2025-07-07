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
                    router.navigate('basicInfo');
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
            link.href = 'Правила конфидециальности.docx';
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
                router.navigate('privacyPolicy');
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

        // Валидация формы
        if (form) {
            form.addEventListener('input', () => {
                this.validateForm();
            });
        }
    }

    async getTelegramData() {
        try {
            if (window.Telegram && window.Telegram.WebApp) {
                const tg = window.Telegram.WebApp;
                return {
                    id: tg.initDataUnsafe?.user?.id || '',
                    first_name: tg.initDataUnsafe?.user?.first_name || '',
                    last_name: tg.initDataUnsafe?.user?.last_name || '',
                    username: tg.initDataUnsafe?.user?.username || '',
                    photo_url: tg.initDataUnsafe?.user?.photo_url || ''
                };
            }
            return null;
        } catch (error) {
            console.error('Ошибка получения данных Telegram:', error);
            return null;
        }
    }

    validateForm() {
        const phone = document.getElementById('phone')?.value?.trim();
        const fullName = document.getElementById('fullName')?.value?.trim();
        const birthDate = document.getElementById('birthDate')?.value;
        const city = document.getElementById('city')?.value?.trim();
        const continueBtn = document.getElementById('continueToDriver');

        // Проверяем обязательные поля
        const isValid = phone && fullName && birthDate && city;
        
        // Дополнительная валидация
        const errors = [];
        
        if (!phone) {
            errors.push('Введите номер телефона');
        } else if (!/^\+?[0-9\s\-\(\)]{10,}$/.test(phone)) {
            errors.push('Неверный формат номера телефона');
        }
        
        if (!fullName) {
            errors.push('Введите полное имя');
        } else if (fullName.length < 2) {
            errors.push('Имя должно содержать минимум 2 символа');
        }
        
        if (!birthDate) {
            errors.push('Выберите дату рождения');
        } else {
            const birth = new Date(birthDate);
            const today = new Date();
            const age = today.getFullYear() - birth.getFullYear();
            if (age < 18 || age > 100) {
                errors.push('Возраст должен быть от 18 до 100 лет');
            }
        }
        
        if (!city) {
            errors.push('Введите город');
        }
        
        // Показываем ошибки
        this.showValidationErrors(errors);
        
        if (continueBtn) {
            continueBtn.disabled = !isValid || errors.length > 0;
        }

        return isValid && errors.length === 0;
    }
    
    showValidationErrors(errors) {
        // Очищаем предыдущие ошибки
        const errorElements = document.querySelectorAll('.validation-error');
        errorElements.forEach(el => el.remove());
        
        // Показываем новые ошибки
        errors.forEach(error => {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'validation-error';
            errorDiv.textContent = error;
            errorDiv.style.color = '#dc3545';
            errorDiv.style.fontSize = '12px';
            errorDiv.style.marginTop = '5px';
            
            // Добавляем ошибку к соответствующему полю
            const fieldMap = {
                'Введите номер телефона': 'phone',
                'Неверный формат номера телефона': 'phone',
                'Введите полное имя': 'fullName',
                'Имя должно содержать минимум 2 символа': 'fullName',
                'Выберите дату рождения': 'birthDate',
                'Возраст должен быть от 18 до 100 лет': 'birthDate',
                'Введите город': 'city'
            };
            
            const fieldName = fieldMap[error];
            if (fieldName) {
                const field = document.getElementById(fieldName);
                if (field && field.parentNode) {
                    field.parentNode.appendChild(errorDiv);
                }
            }
        });
    }

    async validateAndContinue() {
        if (!this.validateForm()) {
            Utils.showNotification('Заполните все обязательные поля корректно', 'error');
            return;
        }

        // Собираем данные формы с валидацией
        const phone = document.getElementById('phone').value.trim();
        const fullName = document.getElementById('fullName').value.trim();
        const birthDate = document.getElementById('birthDate').value;
        const city = document.getElementById('city').value.trim();
        const avatarUrl = document.getElementById('avatarUrl').value;
        
        // Дополнительная проверка данных
        if (!phone || !fullName || !birthDate || !city) {
            Utils.showNotification('Заполните все обязательные поля', 'error');
            return;
        }
        
        this.formData = {
            phone,
            fullName,
            birthDate,
            city,
            avatarUrl
        };

        // Сохраняем данные в состоянии
        stateManager.setState('registrationData', {
            ...stateManager.getState('registrationData'),
            basicInfo: this.formData,
            telegramData: this.telegramData
        });

        router.navigate('driverInfo');
    }

    async uploadAvatar() {
        try {
            // Создаем input для выбора файла
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (file) {
                    try {
                        // Загружаем файл
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        const response = await API.uploadFile(formData);
                        
                        if (response.success) {
                            document.getElementById('avatarUrl').value = response.url;
                            document.getElementById('avatarPreview').innerHTML = 
                                `<img src="${response.url}" alt="Аватар">`;
                            
                            Utils.showNotification('Успех', 'Аватар загружен', 'success');
                        }
                    } catch (error) {
                        console.error('Ошибка загрузки аватара:', error);
                        Utils.showNotification('Ошибка', 'Не удалось загрузить аватар', 'error');
                    }
                }
            };
            
            input.click();
        } catch (error) {
            console.error('Ошибка выбора файла:', error);
            Utils.showNotification('Ошибка', 'Не удалось выбрать файл', 'error');
        }
    }
}

// Экран водительских данных
class DriverInfoScreen {
    constructor() {
        this.formData = {
            carBrand: '',
            carModel: '',
            carYear: '',
            carColor: '',
            driverLicenseNumber: '',
            driverLicensePhotoUrl: '',
            carPhotoUrl: ''
        };
        this.isDriver = false;
    }

    render() {
        return `
            <div class="registration-container">
                <div class="registration-header">
                    <h1 class="section-title">Водительские данные</h1>
                    <p class="text-muted">Заполните информацию об автомобиле (необязательно)</p>
                </div>
                
                <div class="driver-toggle">
                    <label class="toggle-container">
                        <input type="checkbox" id="isDriver" ${this.isDriver ? 'checked' : ''}>
                        <span class="toggle-slider"></span>
                        <span class="toggle-text">Я хочу быть водителем</span>
                    </label>
                </div>
                
                <form id="driverInfoForm" class="registration-form" ${!this.isDriver ? 'style="display: none;"' : ''}>
                    <div class="form-row">
                        <div class="form-group">
                            <label for="carBrand">Марка автомобиля</label>
                            <input type="text" id="carBrand" placeholder="LADA">
                        </div>
                        <div class="form-group">
                            <label for="carModel">Модель автомобиля</label>
                            <input type="text" id="carModel" placeholder="Granta">
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="carYear">Год выпуска</label>
                            <input type="number" id="carYear" min="1900" max="${new Date().getFullYear() + 1}" placeholder="2023">
                        </div>
                        <div class="form-group">
                            <label for="carColor">Цвет автомобиля</label>
                            <input type="text" id="carColor" placeholder="Серый">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="driverLicenseNumber">Номер водительского удостоверения</label>
                        <input type="text" id="driverLicenseNumber" placeholder="12 34 567890">
                    </div>
                    
                    <div class="form-group">
                        <label>Фото водительского удостоверения</label>
                        <div class="file-upload">
                            <button type="button" class="btn btn-secondary" id="uploadLicense">
                                Загрузить фото удостоверения
                            </button>
                            <div class="file-preview" id="licensePreview"></div>
                        </div>
                        <input type="hidden" id="driverLicensePhotoUrl">
                    </div>
                    
                    <div class="form-group">
                        <label>Фото автомобиля</label>
                        <div class="file-upload">
                            <button type="button" class="btn btn-secondary" id="uploadCarPhoto">
                                Загрузить фото автомобиля
                            </button>
                            <div class="file-preview" id="carPhotoPreview"></div>
                        </div>
                        <input type="hidden" id="carPhotoUrl">
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
        const isDriverToggle = document.getElementById('isDriver');
        const driverForm = document.getElementById('driverInfoForm');
        const backBtn = document.getElementById('backToBasic');
        const completeBtn = document.getElementById('completeRegistration');
        const uploadLicenseBtn = document.getElementById('uploadLicense');
        const uploadCarPhotoBtn = document.getElementById('uploadCarPhoto');

        if (isDriverToggle) {
            isDriverToggle.addEventListener('change', (e) => {
                this.isDriver = e.target.checked;
                if (driverForm) {
                    driverForm.style.display = this.isDriver ? 'block' : 'none';
                }
            });
        }

        if (backBtn) {
            backBtn.addEventListener('click', () => {
                router.navigate('basicInfo');
            });
        }

        if (completeBtn) {
            completeBtn.addEventListener('click', () => {
                this.completeRegistration();
            });
        }

        if (uploadLicenseBtn) {
            uploadLicenseBtn.addEventListener('click', () => {
                this.uploadFile('driverLicensePhotoUrl', 'licensePreview');
            });
        }

        if (uploadCarPhotoBtn) {
            uploadCarPhotoBtn.addEventListener('click', () => {
                this.uploadFile('carPhotoUrl', 'carPhotoPreview');
            });
        }
    }

    async uploadFile(inputId, previewId) {
        try {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            
            input.onchange = async (e) => {
                const file = e.target.files[0];
                if (file) {
                    try {
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        const response = await API.uploadFile(formData);
                        
                        if (response.success) {
                            document.getElementById(inputId).value = response.url;
                            document.getElementById(previewId).innerHTML = 
                                `<img src="${response.url}" alt="Загруженное фото" style="max-width: 100px; max-height: 100px;">`;
                            
                            Utils.showNotification('Успех', 'Фото загружено', 'success');
                        }
                    } catch (error) {
                        console.error('Ошибка загрузки файла:', error);
                        Utils.showNotification('Ошибка', 'Не удалось загрузить файл', 'error');
                    }
                }
            };
            
            input.click();
        } catch (error) {
            console.error('Ошибка выбора файла:', error);
            Utils.showNotification('Ошибка', 'Не удалось выбрать файл', 'error');
        }
    }

    async completeRegistration() {
        try {
            // Собираем данные формы
            if (this.isDriver) {
                this.formData = {
                    carBrand: document.getElementById('carBrand').value,
                    carModel: document.getElementById('carModel').value,
                    carYear: document.getElementById('carYear').value,
                    carColor: document.getElementById('carColor').value,
                    driverLicenseNumber: document.getElementById('driverLicenseNumber').value,
                    driverLicensePhotoUrl: document.getElementById('driverLicensePhotoUrl').value,
                    carPhotoUrl: document.getElementById('carPhotoUrl').value
                };
            }

            // Получаем данные регистрации
            const registrationData = stateManager.getState('registrationData');
            
            // Формируем данные для отправки
            const userData = {
                telegram_id: registrationData.telegramData.id,
                phone: registrationData.basicInfo.phone,
                full_name: registrationData.basicInfo.fullName,
                birth_date: registrationData.basicInfo.birthDate,
                city: registrationData.basicInfo.city,
                avatar_url: registrationData.basicInfo.avatarUrl,
                privacy_policy_accepted: true,
                driver_data: this.isDriver ? this.formData : null
            };

            // Отправляем запрос на регистрацию
            const response = await API.registerUser(userData);
            
            if (response.success) {
                // Обновляем данные пользователя в состоянии
                stateManager.updateUserData(response.user);
                
                Utils.showNotification('Успех', 'Регистрация завершена!', 'success');
                
                // Переходим к основному экрану
                router.navigate('findRide');
            }
            
        } catch (error) {
            console.error('Ошибка регистрации:', error);
            Utils.showNotification('Ошибка', 'Не удалось завершить регистрацию', 'error');
        }
    }
}

// Экран успешной регистрации
class RegistrationSuccessScreen {
    render() {
        return `
            <div class="success-container">
                <div class="success-icon">✅</div>
                <h1 class="section-title">Регистрация завершена!</h1>
                <p class="text-muted">Добро пожаловать в сервис поиска попутчиков</p>
                
                <div class="success-actions">
                    <button class="btn btn-primary btn-full" id="startUsing">
                        Начать использование
                    </button>
                </div>
            </div>
        `;
    }

    setupEventHandlers() {
        const startBtn = document.getElementById('startUsing');
        
        if (startBtn) {
            startBtn.addEventListener('click', () => {
                router.navigate('findRide');
            });
        }
    }
}

export default {
    privacyPolicy: PrivacyPolicyScreen,
    basicInfo: BasicInfoScreen,
    driverInfo: DriverInfoScreen,
    registrationSuccess: RegistrationSuccessScreen
}; 