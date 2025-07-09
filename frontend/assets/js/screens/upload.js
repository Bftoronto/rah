import { stateManager } from '../state.js';

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
        this.setupImageUpload('avatarInput', 'avatarPreview', 'avatarProgress', 'avatarProgressBar', 'uploadAvatarBtn', (url) => {
            const userData = this.stateManager.getUserData();
            userData.avatar = url;
            this.stateManager.updateUserData(userData);
            window.utils.showNotification('Успех', 'Фото профиля загружено', 'success');
            window.router.navigate('profile');
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
        
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            // Показываем превью
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
                button.disabled = false;
            };
            reader.readAsDataURL(file);
        });
        
        button.addEventListener('click', () => {
            const file = input.files[0];
            if (!file) return;
            
            button.disabled = true;
            progress.style.display = 'block';
            
            window.utils.uploadImage(file, 
                (progressValue) => {
                    progressBar.style.width = `${progressValue}%`;
                },
                (url) => {
                    onSuccess(url);
                },
                (error) => {
                    window.utils.showNotification('Ошибка', error, 'error');
                    button.disabled = false;
                    progress.style.display = 'none';
                }
            );
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
        this.setupImageUpload('carPhotoInput', 'carPhotoPreview', 'carPhotoProgress', 'carPhotoProgressBar', 'uploadCarPhotoBtn', (url) => {
            const userData = this.stateManager.getUserData();
            userData.car.photo = url;
            this.stateManager.updateUserData(userData);
            window.utils.showNotification('Успех', 'Фото автомобиля загружено', 'success');
            window.router.navigate('profile');
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
        
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            // Показываем превью
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
                button.disabled = false;
            };
            reader.readAsDataURL(file);
        });
        
        button.addEventListener('click', () => {
            const file = input.files[0];
            if (!file) return;
            
            button.disabled = true;
            progress.style.display = 'block';
            
            window.utils.uploadImage(file, 
                (progressValue) => {
                    progressBar.style.width = `${progressValue}%`;
                },
                (url) => {
                    onSuccess(url);
                },
                (error) => {
                    window.utils.showNotification('Ошибка', error, 'error');
                    button.disabled = false;
                    progress.style.display = 'none';
                }
            );
        });
    }
}

export default UploadAvatarScreen;
export { UploadCarPhotoScreen }; 