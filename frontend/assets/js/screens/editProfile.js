import { stateManager } from '../state.js';

class EditProfileScreen {
    constructor() {
        this.stateManager = stateManager;
    }

    render() {
        const user = this.stateManager.getUserData();
        return `
            <h2 class="section-title">Редактировать профиль</h2>
            
            <div class="form-group">
                <label class="form-label">Имя</label>
                <input type="text" class="form-control" id="editNameInput" value="${user.name}">
            </div>
            
            <div class="form-group">
                <label class="form-label">О себе</label>
                <textarea class="form-control" id="editAboutInput" rows="3" placeholder="Расскажите о себе" maxlength="200">${user.about || 'Пунктуальный, люблю слушать музыку и разговаривать обо всем'}</textarea>
                <div class="form-char-counter" id="aboutCharCounter">0/200</div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Автомобиль</label>
                <input type="text" class="form-control" id="editCarModelInput" value="${user.car.model}">
            </div>
            
            <div class="d-flex justify-between">
                <div class="form-group" style="width: 48%;">
                    <label class="form-label">Год выпуска</label>
                    <input type="number" class="form-control" id="editCarYearInput" value="${user.car.year}">
                </div>
                
                <div class="form-group" style="width: 48%;">
                    <label class="form-label">Цвет</label>
                    <input type="text" class="form-control" id="editCarColorInput" value="${user.car.color}">
                </div>
            </div>
            
            <div class="form-group">
                <label class="form-label">Номер автомобиля</label>
                <input type="text" class="form-control" id="editCarPlateInput" value="${user.car.plate}">
            </div>

            <div class="form-group">
                <label class="form-label">Фото автомобиля</label>
                <div style="display:flex;flex-direction:column;align-items:center;gap:10px;width:100%;">
                    <img id="editCarPhotoPreview" src="${user.car.photo || ''}" alt="Фото автомобиля" style="max-width:220px;max-height:120px;border-radius:10px;object-fit:cover;display:${user.car.photo ? 'block' : 'none'};background:#f8f8f8;"/>
                    <div id="carPhotoActions" style="width:100%;display:flex;gap:10px;">
                        <button type="button" id="editCarPhotoBtn" class="btn btn-blue" style="width:100%;margin:0 0 8px 0;">Добавить файл</button>
                        ${user.car.photo ? '<button type="button" id="deleteCarPhotoBtn" class="btn btn-outline" style="width:100%;margin:0 0 8px 0;color:#f65446;border-color:#f65446;">Удалить фото</button>' : ''}
                    </div>
                    <input type="file" id="editCarPhotoInput" accept="image/*" style="display:none;">
                </div>
            </div>
            
            <button class="btn btn-primary mt-20" id="saveProfileBtn">Сохранить</button>
            <button class="btn btn-outline mt-10" id="cancelEditBtn">Отмена</button>
        `;
    }

    setupEventHandlers() {
        // Сохранение профиля
        const saveBtn = document.getElementById('saveProfileBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                window.utils.clearFormErrors();
                
                const formData = {
                    editNameInput: document.getElementById('editNameInput').value,
                    editAboutInput: document.getElementById('editAboutInput').value,
                    editCarModelInput: document.getElementById('editCarModelInput').value,
                    editCarYearInput: document.getElementById('editCarYearInput').value,
                    editCarColorInput: document.getElementById('editCarColorInput').value,
                    editCarPlateInput: document.getElementById('editCarPlateInput').value,
                    editCarPhotoInput: document.getElementById('editCarPhotoInput').files[0]
                };
                
                const rules = {
                    editNameInput: { required: true, minLength: 2 },
                    editAboutInput: { required: false, maxLength: 200 },
                    editCarModelInput: { required: true, minLength: 2 },
                    editCarYearInput: { required: true },
                    editCarColorInput: { required: true },
                    editCarPlateInput: { required: true, minLength: 5 }
                };
                
                const validation = window.utils.validateForm(formData, rules);
                
                if (!validation.isValid) {
                    window.utils.showFormErrors(validation.errors);
                    window.utils.showNotification('Ошибка', 'Пожалуйста, исправьте ошибки в форме', 'error');
                    return;
                }
                
                // Обновляем данные пользователя
                const userData = this.stateManager.getUserData();
                userData.name = formData.editNameInput;
                userData.about = formData.editAboutInput;
                userData.car.model = formData.editCarModelInput;
                userData.car.year = parseInt(formData.editCarYearInput);
                userData.car.color = formData.editCarColorInput;
                userData.car.plate = formData.editCarPlateInput;
                // Фото автомобиля
                if (formData.editCarPhotoInput) {
                    // Сохраняем фото как base64 (или можно реализовать upload на сервер, если есть uploadImage)
                    const reader = new FileReader();
                    reader.onload = (e) => {
                        userData.car.photo = e.target.result;
                        this.stateManager.updateUserData(userData);
                        window.utils.showNotification('Успех', 'Профиль успешно обновлен!', 'success');
                        window.router.navigate('profile');
                    };
                    reader.readAsDataURL(formData.editCarPhotoInput);
                    return;
                }
                this.stateManager.updateUserData(userData);
                window.utils.showNotification('Успех', 'Профиль успешно обновлен!', 'success');
                window.router.navigate('profile');
            });
        }

        // Отмена редактирования
        const cancelBtn = document.getElementById('cancelEditBtn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                window.router.navigate('profile');
            });
        }

        // Валидация в реальном времени
        ['editNameInput', 'editAboutInput', 'editCarModelInput', 'editCarYearInput', 'editCarColorInput', 'editCarPlateInput'].forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('blur', () => {
                    const value = field.value;
                    let rules = { required: true, minLength: 2 };
                    
                    if (fieldId === 'editAboutInput') {
                        rules = { required: false, maxLength: 200 };
                    } else if (fieldId === 'editCarPlateInput') {
                        rules = { required: true, minLength: 5 };
                    } else if (fieldId === 'editCarYearInput') {
                        rules = { required: true };
                    }
                    
                    const errors = window.utils.validateField(value, rules);
                    
                    if (errors.length > 0) {
                        window.utils.showFieldError(field, errors[0]);
                    } else {
                        window.utils.hideFieldError(field);
                    }
                });
                
                field.addEventListener('input', () => {
                    window.utils.hideFieldError(field);
                    
                    // Обновляем счетчик символов для поля "О себе"
                    if (fieldId === 'editAboutInput') {
                        const charCounter = document.getElementById('aboutCharCounter');
                        if (charCounter) {
                            const currentLength = field.value.length;
                            charCounter.textContent = `${currentLength}/200`;
                            
                            // Меняем цвет при приближении к лимиту
                            if (currentLength > 180) {
                                charCounter.style.color = '#e74c3c';
                            } else if (currentLength > 150) {
                                charCounter.style.color = '#f39c12';
                            } else {
                                charCounter.style.color = '#888';
                            }
                        }
                    }
                });
            }
        });
        
        // Инициализация счетчика символов
        const aboutInput = document.getElementById('editAboutInput');
        const charCounter = document.getElementById('aboutCharCounter');
        if (aboutInput && charCounter) {
            const currentLength = aboutInput.value.length;
            charCounter.textContent = `${currentLength}/200`;
        }

        // Превью фото автомобиля при выборе файла
        const carPhotoInput = document.getElementById('editCarPhotoInput');
        const carPhotoPreview = document.getElementById('editCarPhotoPreview');
        const carPhotoBtn = document.getElementById('editCarPhotoBtn');
        const deleteCarPhotoBtn = document.getElementById('deleteCarPhotoBtn');
        if (carPhotoBtn && carPhotoInput) {
            carPhotoBtn.addEventListener('click', () => carPhotoInput.click());
        }
        if (carPhotoInput && carPhotoPreview) {
            carPhotoInput.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (!file) return;
                const reader = new FileReader();
                reader.onload = (ev) => {
                    carPhotoPreview.src = ev.target.result;
                    carPhotoPreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            });
        }
        if (deleteCarPhotoBtn && carPhotoPreview && carPhotoInput) {
            deleteCarPhotoBtn.addEventListener('click', () => {
                carPhotoPreview.src = '';
                carPhotoPreview.style.display = 'none';
                carPhotoInput.value = '';
                // Удаляем фото из userData сразу (чтобы не осталось после сохранения)
                const userData = this.stateManager.getUserData();
                userData.car.photo = '';
                this.stateManager.updateUserData(userData);
                // Перерисовываем форму для скрытия кнопки
                window.router.navigate('editProfile');
            });
        }
    }
}

export default EditProfileScreen; 