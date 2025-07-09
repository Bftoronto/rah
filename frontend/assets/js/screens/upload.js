import { stateManager } from '../state.js';
import { API } from '../api.js';
import { Utils } from '../utils.js';

class UploadAvatarScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        return `
            <h2 class="section-title">Загрузка фото профиля</h2>
            
            <div class="image-upload" id="avatarUpload">
                <input type="file" id="avatarInput" accept="image/*">
                <div class="upload-icon">
                    <i class="fas fa-user-circle"></i>
                </div>
                <div class="upload-text">
                    Нажмите или перетащите фото сюда<br>
                    <small>JPG, PNG до 5MB</small>
                </div>
            </div>
            
            <img class="image-preview" id="avatarPreview">
            <div class="upload-progress" id="avatarProgress">
                <div class="upload-progress-bar" id="avatarProgressBar"></div>
            </div>
            
            <div class="alert alert-warning mt-20">
                <i class="fas fa-info-circle"></i>
                Фото профиля поможет другим пользователям узнать вас
            </div>
            
            <button class="btn btn-primary mt-20" id="uploadAvatarBtn" disabled>Загрузить фото</button>
            <button class="btn btn-outline mt-10" id="skipAvatarBtn">Пропустить</button>
        `;
    }

    setupEventHandlers() {
        this.setupImageUpload('avatarInput', 'avatarPreview', 'avatarProgress', 'avatarProgressBar', 'uploadAvatarBtn', async (file) => {
            try {
                // Используем новый API для загрузки
                const response = await API.uploadFile(file, 'avatar');
                
                if (response.success) {
                    // Обновляем данные пользователя
                    const userData = this.stateManager.getUserData();
                    userData.avatar_url = response.file_url;
                    this.stateManager.updateUserData(userData);
                    
                    Utils.showNotification('Успех', 'Фото профиля загружено', 'success');
                    window.router.navigate('profile');
                } else {
                    throw new Error(response.message || 'Ошибка загрузки');
                }
            } catch (error) {
                Utils.handleApiError(error, 'uploadAvatar');
            }
        });
        
        const skipBtn = document.getElementById('skipAvatarBtn');
        if (skipBtn) {
            skipBtn.addEventListener('click', () => {
                window.router.navigate('profile');
            });
        }
    }

    setupImageUpload(inputId, previewId, progressId, progressBarId, buttonId, onSuccess) {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);
        const progress = document.getElementById(progressId);
        const progressBar = document.getElementById(progressBarId);
        const button = document.getElementById(buttonId);
        
        if (!input || !preview || !progress || !progressBar || !button) return;
        
        input.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            // Валидация файла
            const validation = Utils.validateField(file, {
                fileSize: 5 * 1024 * 1024, // 5MB
                fileType: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            });
            
            if (validation.length > 0) {
                Utils.showNotification('Ошибка', validation[0], 'error');
                return;
            }
            
            // Показываем превью
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
                button.disabled = false;
            };
            reader.readAsDataURL(file);
        });
        
        button.addEventListener('click', async () => {
            const file = input.files[0];
            if (!file) return;
            
            button.disabled = true;
            progress.style.display = 'block';
            
            try {
                // Оптимизируем изображение перед загрузкой
                const optimizedFile = await Utils.optimizeImage(file, 1024, 0.8);
                
                // Имитируем прогресс загрузки
                let progressValue = 0;
                const progressInterval = setInterval(() => {
                    progressValue += Math.random() * 20;
                    if (progressValue >= 100) {
                        progressValue = 100;
                        clearInterval(progressInterval);
                    }
                    progressBar.style.width = `${progressValue}%`;
                }, 100);
                
                // Вызываем callback с оптимизированным файлом
                await onSuccess(optimizedFile);
                
            } catch (error) {
                Utils.showNotification('Ошибка', error.message, 'error');
                button.disabled = false;
                progress.style.display = 'none';
            }
        });
    }
}

class UploadCarPhotoScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        return `
            <h2 class="section-title">Фото автомобиля</h2>
            
            <div class="image-upload" id="carPhotoUpload">
                <input type="file" id="carPhotoInput" accept="image/*">
                <div class="upload-icon">
                    <i class="fas fa-car"></i>
                </div>
                <div class="upload-text">
                    Загрузите фото вашего автомобиля<br>
                    <small>JPG, PNG до 5MB</small>
                </div>
            </div>
            
            <img class="image-preview" id="carPhotoPreview">
            <div class="upload-progress" id="carPhotoProgress">
                <div class="upload-progress-bar" id="carPhotoProgressBar"></div>
            </div>
            
            <div class="alert alert-warning mt-20">
                <i class="fas fa-info-circle"></i>
                Фото автомобиля увеличивает доверие пассажиров
            </div>
            
            <button class="btn btn-primary mt-20" id="uploadCarPhotoBtn" disabled>Загрузить фото</button>
            <button class="btn btn-outline mt-10" id="skipCarPhotoBtn">Пропустить</button>
        `;
    }

    setupEventHandlers() {
        this.setupImageUpload('carPhotoInput', 'carPhotoPreview', 'carPhotoProgress', 'carPhotoProgressBar', 'uploadCarPhotoBtn', async (file) => {
            try {
                // Используем новый API для загрузки
                const response = await API.uploadFile(file, 'car');
                
                if (response.success) {
                    // Обновляем данные пользователя
                    const userData = this.stateManager.getUserData();
                    userData.car_photo_url = response.file_url;
                    this.stateManager.updateUserData(userData);
                    
                    Utils.showNotification('Успех', 'Фото автомобиля загружено', 'success');
                    window.router.navigate('profile');
                } else {
                    throw new Error(response.message || 'Ошибка загрузки');
                }
            } catch (error) {
                Utils.handleApiError(error, 'uploadCarPhoto');
            }
        });
        
        const skipBtn = document.getElementById('skipCarPhotoBtn');
        if (skipBtn) {
            skipBtn.addEventListener('click', () => {
                window.router.navigate('profile');
            });
        }
    }

    setupImageUpload(inputId, previewId, progressId, progressBarId, buttonId, onSuccess) {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);
        const progress = document.getElementById(progressId);
        const progressBar = document.getElementById(progressBarId);
        const button = document.getElementById(buttonId);
        
        if (!input || !preview || !progress || !progressBar || !button) return;
        
        input.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            // Валидация файла
            const validation = Utils.validateField(file, {
                fileSize: 5 * 1024 * 1024, // 5MB
                fileType: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            });
            
            if (validation.length > 0) {
                Utils.showNotification('Ошибка', validation[0], 'error');
                return;
            }
            
            // Показываем превью
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
                button.disabled = false;
            };
            reader.readAsDataURL(file);
        });
        
        button.addEventListener('click', async () => {
            const file = input.files[0];
            if (!file) return;
            
            button.disabled = true;
            progress.style.display = 'block';
            
            try {
                // Оптимизируем изображение перед загрузкой
                const optimizedFile = await Utils.optimizeImage(file, 1024, 0.8);
                
                // Имитируем прогресс загрузки
                let progressValue = 0;
                const progressInterval = setInterval(() => {
                    progressValue += Math.random() * 20;
                    if (progressValue >= 100) {
                        progressValue = 100;
                        clearInterval(progressInterval);
                    }
                    progressBar.style.width = `${progressValue}%`;
                }, 100);
                
                // Вызываем callback с оптимизированным файлом
                await onSuccess(optimizedFile);
                
            } catch (error) {
                Utils.showNotification('Ошибка', error.message, 'error');
                button.disabled = false;
                progress.style.display = 'none';
            }
        });
    }
}

class UploadDriverLicenseScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        return `
            <h2 class="section-title">Фото водительских прав</h2>
            
            <div class="image-upload" id="licenseUpload">
                <input type="file" id="licenseInput" accept="image/*">
                <div class="upload-icon">
                    <i class="fas fa-id-card"></i>
                </div>
                <div class="upload-text">
                    Загрузите фото водительских прав<br>
                    <small>JPG, PNG до 5MB</small>
                </div>
            </div>
            
            <img class="image-preview" id="licensePreview">
            <div class="upload-progress" id="licenseProgress">
                <div class="upload-progress-bar" id="licenseProgressBar"></div>
            </div>
            
            <div class="alert alert-warning mt-20">
                <i class="fas fa-info-circle"></i>
                Фото водительских прав необходимо для подтверждения статуса водителя
            </div>
            
            <button class="btn btn-primary mt-20" id="uploadLicenseBtn" disabled>Загрузить фото</button>
            <button class="btn btn-outline mt-10" id="skipLicenseBtn">Пропустить</button>
        `;
    }

    setupEventHandlers() {
        this.setupImageUpload('licenseInput', 'licensePreview', 'licenseProgress', 'licenseProgressBar', 'uploadLicenseBtn', async (file) => {
            try {
                // Используем новый API для загрузки
                const response = await API.uploadFile(file, 'license');
                
                if (response.success) {
                    // Обновляем данные пользователя
                    const userData = this.stateManager.getUserData();
                    userData.driver_license_photo_url = response.file_url;
                    this.stateManager.updateUserData(userData);
                    
                    Utils.showNotification('Успех', 'Фото водительских прав загружено', 'success');
                    window.router.navigate('profile');
                } else {
                    throw new Error(response.message || 'Ошибка загрузки');
                }
            } catch (error) {
                Utils.handleApiError(error, 'uploadDriverLicense');
            }
        });
        
        const skipBtn = document.getElementById('skipLicenseBtn');
        if (skipBtn) {
            skipBtn.addEventListener('click', () => {
                window.router.navigate('profile');
            });
        }
    }

    setupImageUpload(inputId, previewId, progressId, progressBarId, buttonId, onSuccess) {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);
        const progress = document.getElementById(progressId);
        const progressBar = document.getElementById(progressBarId);
        const button = document.getElementById(buttonId);
        
        if (!input || !preview || !progress || !progressBar || !button) return;
        
        input.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            // Валидация файла
            const validation = Utils.validateField(file, {
                fileSize: 5 * 1024 * 1024, // 5MB
                fileType: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            });
            
            if (validation.length > 0) {
                Utils.showNotification('Ошибка', validation[0], 'error');
                return;
            }
            
            // Показываем превью
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
                button.disabled = false;
            };
            reader.readAsDataURL(file);
        });
        
        button.addEventListener('click', async () => {
            const file = input.files[0];
            if (!file) return;
            
            button.disabled = true;
            progress.style.display = 'block';
            
            try {
                // Оптимизируем изображение перед загрузкой
                const optimizedFile = await Utils.optimizeImage(file, 1024, 0.8);
                
                // Имитируем прогресс загрузки
                let progressValue = 0;
                const progressInterval = setInterval(() => {
                    progressValue += Math.random() * 20;
                    if (progressValue >= 100) {
                        progressValue = 100;
                        clearInterval(progressInterval);
                    }
                    progressBar.style.width = `${progressValue}%`;
                }, 100);
                
                // Вызываем callback с оптимизированным файлом
                await onSuccess(optimizedFile);
                
            } catch (error) {
                Utils.showNotification('Ошибка', error.message, 'error');
                button.disabled = false;
                progress.style.display = 'none';
            }
        });
    }
}

export default UploadAvatarScreen;
export { UploadCarPhotoScreen, UploadDriverLicenseScreen }; 