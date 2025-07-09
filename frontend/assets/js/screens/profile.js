import { stateManager } from '../state.js';

class ProfileScreen {
    constructor() {
        this.stateManager = stateManager;
        this.state = stateManager.getUserData();
        this.activeTab = 'about'; // По умолчанию активен таб "О себе"
    }

    render() {
        const user = this.state;
        return `
        <div class="profile-new" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
            <div class="profile-main-block">
                <div class="profile-avatar-block">
                    <div class="profile-avatar-new" id="profileAvatar">
                        ${user.avatar ? `<img src="${user.avatar}" alt="Фото профиля">` : `<span>${user.name.split(' ').map(n => n[0]).join('')}</span>`}
                        <div class="profile-avatar-edit">
                            <i class="fas fa-camera"></i>
                        </div>
                    </div>
                    <div class="profile-main-info">
                        <div class="profile-main-name">${user.name}</div>
                    </div>
                </div>
                <div class="profile-main-links">
                    <div class="profile-link" id="editProfileBtn">Редактировать профиль <i class="fas fa-chevron-right"></i></div>
                    <div class="profile-link" id="notificationSettingsBtn">Настройки уведомлений <i class="fas fa-chevron-right"></i></div>
                </div>
                <div class="profile-balance-rating-new">
                    <div class="profile-balance-label">Ваш баланс</div>
                    <div class="profile-balance-value-new">${user.balance} <span class="profile-currency">₽</span></div>
                    <div class="profile-rating-label">Рейтинг отмены поездок</div>
                    <div class="profile-rating-value-new">${user.cancelledRides || 0}%</div>
                </div>
                <div class="profile-tabs-new">
                    <button class="profile-tab-new ${this.activeTab === 'about' ? 'active' : ''}" data-tab="about">О себе</button>
                    <button class="profile-tab-new ${this.activeTab === 'documents' ? 'active' : ''}" data-tab="documents">Документы</button>
                    <button class="profile-tab-new ${this.activeTab === 'account' ? 'active' : ''}" data-tab="account">Учетная запись</button>
                </div>
                
                <!-- Контент таба "О себе" -->
                <div class="profile-tab-content ${this.activeTab === 'about' ? 'active' : ''}" data-tab="about">
                    <div class="profile-checklist-block">
                        <div class="profile-check-item" data-status="verified">
                            <span class="profile-check-icon">✔</span> Паспорт подтвержден
                        </div>
                        <div class="profile-check-item" data-status="verified">
                            <span class="profile-check-icon">✔</span> Номер телефона подтвержден
                        </div>
                        <div class="profile-check-item" data-status="verified">
                            <span class="profile-check-icon">✔</span> Автомобиль проверен
                        </div>
                        <div class="profile-check-item" data-status="pending">
                            <span class="profile-check-icon">⏳</span> Водительские права на проверке
                        </div>
                    </div>
                    <div class="profile-section-block">
                        <div class="profile-section-title">О себе</div>
                        <div class="profile-section-text">${user.about || 'Пунктуальный, люблю слушать музыку и разговаривать обо всем'}</div>
                    </div>
                    <div class="profile-section-block">
                        <div class="profile-section-title">Автомобиль</div>
                        <div class="profile-car-photo-block" style="display:flex;flex-direction:column;align-items:center;gap:10px;">
                            ${user.car.photo ? `<img src="${user.car.photo}" class="profile-car-photo-new" alt="Фото автомобиля" style="max-width:220px;max-height:120px;border-radius:10px;object-fit:cover;background:#f8f8f8;"/>` : ''}
                        </div>
                        <div class="profile-car-info-new">
                            <span>${user.car.model}, ${user.car.year}</span>
                            <span class="profile-car-plate-new">${user.car.plate}</span>
                        </div>
                    </div>
                    <div class="profile-section-block" style="margin-top:18px;">
                        <div class="profile-section-title">Способы оплаты</div>
                        <div class="profile-section-text" aria-label="Способы оплаты">
                            <span role="img" aria-label="наличные">💵</span> Наличный расчет <span style="color:#bbb;">|</span> <span role="img" aria-label="перевод на карту">💳</span> Перевод на карту<br>
                            <span style="font-size:13px;color:#888;">Все расчеты осуществляются напрямую между пассажиром и водителем</span>
                        </div>
                    </div>
                </div>
                
                <!-- Контент таба "Документы" -->
                <div class="profile-tab-content ${this.activeTab === 'documents' ? 'active' : ''}" data-tab="documents">
                    <div class="profile-documents-section">
                        <div class="profile-document-item">
                            <div class="profile-document-icon">
                                <i class="fas fa-id-card"></i>
                            </div>
                            <div class="profile-document-info">
                                <div class="profile-document-name">Паспорт РФ</div>
                                <div class="profile-document-status profile-status-verified">Подтвержден</div>
                            </div>
                            <div class="profile-document-date">15.03.2024</div>
                        </div>
                        <div class="profile-document-item">
                            <div class="profile-document-icon">
                                <i class="fas fa-car"></i>
                            </div>
                            <div class="profile-document-info">
                                <div class="profile-document-name">Водительские права</div>
                                <div class="profile-document-status profile-status-pending">На проверке</div>
                            </div>
                            <div class="profile-document-date">20.03.2024</div>
                        </div>
                        <div class="profile-document-item">
                            <div class="profile-document-icon">
                                <i class="fas fa-file-alt"></i>
                            </div>
                            <div class="profile-document-info">
                                <div class="profile-document-name">СТС автомобиля</div>
                                <div class="profile-document-status profile-status-verified">Подтвержден</div>
                            </div>
                            <div class="profile-document-date">18.03.2024</div>
                        </div>
                    </div>
                </div>
                <!-- Контент таба "Учетная запись" -->
                <div class="profile-tab-content ${this.activeTab === 'account' ? 'active' : ''}" data-tab="account">
                    <div class="profile-account-section">
                        <div class="profile-account-item">
                            <div class="profile-account-label">Email</div>
                            <div class="profile-account-value">${user.email || 'user@example.com'}</div>
                        </div>
                        <div class="profile-account-item">
                            <div class="profile-account-label">Телефон</div>
                            <div class="profile-account-value">${user.phone || '+7 (999) 123-45-67'}</div>
                        </div>
                        <div class="profile-account-item">
                            <div class="profile-account-label">Дата регистрации</div>
                            <div class="profile-account-value">${user.registrationDate || '15.03.2024'}</div>
                        </div>
                        <div class="profile-account-item">
                            <div class="profile-account-label">Статус аккаунта</div>
                            <div class="profile-account-value profile-status-active">Активен</div>
                        </div>
                    </div>
                    <button id="deleteAccountBtn" style="width:100%;margin-top:24px;padding:14px 0;background:#f65446;color:#fff;font-size:16px;font-weight:600;border:none;border-radius:12px;box-shadow:0 2px 8px rgba(246,84,70,0.08);transition:background 0.2s;cursor:pointer;">Удалить запись</button>
                </div>
            </div>
        </div>
        `;
    }

    setupEventHandlers() {
        // Смена аватара
        const avatarElement = document.getElementById('profileAvatar');
        if (avatarElement) {
            avatarElement.addEventListener('click', () => {
                this.changeAvatar();
            });
        }

        // Переключение табов
        const tabButtons = document.querySelectorAll('.profile-tab-new');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.target.dataset.tab;
                this.switchTab(tabName);
            });
        });

        // Редактирование профиля
        const editProfileBtn = document.getElementById('editProfileBtn');
        if (editProfileBtn) {
            editProfileBtn.addEventListener('click', () => {
                window.router.navigate('editProfile');
            });
        }

        // Настройки уведомлений
        const notificationSettingsBtn = document.getElementById('notificationSettingsBtn');
        if (notificationSettingsBtn) {
            notificationSettingsBtn.addEventListener('click', () => {
                window.router.navigate('notificationSettings');
            });
        }

        // Обработчик кнопки удаления аккаунта
        const deleteBtn = document.getElementById('deleteAccountBtn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                this.showDeleteModal();
            });
        }

        // Анимация чек-листа
        this.animateChecklist();
    }

    changeAvatar() {
        // Создаем скрытый input для выбора файла
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.style.display = 'none';
        
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            // Показываем превью
            const reader = new FileReader();
            reader.onload = (e) => {
                const avatarImg = document.querySelector('#profileAvatar img');
                if (avatarImg) {
                    avatarImg.src = e.target.result;
                } else {
                    const avatarSpan = document.querySelector('#profileAvatar span');
                    if (avatarSpan) {
                        avatarSpan.style.display = 'none';
                        const newImg = document.createElement('img');
                        newImg.src = e.target.result;
                        newImg.alt = 'Фото профиля';
                        document.getElementById('profileAvatar').appendChild(newImg);
                    }
                }
                
                // Обновляем данные пользователя
                const userData = this.stateManager.getUserData();
                userData.avatar = e.target.result;
                this.stateManager.updateUserData(userData);
                
                window.utils.showNotification('Успех', 'Фото профиля обновлено', 'success');
            };
            reader.readAsDataURL(file);
        });
        
        document.body.appendChild(input);
        input.click();
        document.body.removeChild(input);
    }

    switchTab(tabName) {
        // Обновляем активный таб
        this.activeTab = tabName;
        
        // Обновляем кнопки табов
        const tabButtons = document.querySelectorAll('.profile-tab-new');
        tabButtons.forEach(button => {
            button.classList.remove('active');
            if (button.dataset.tab === tabName) {
                button.classList.add('active');
            }
        });
        
        // Обновляем контент табов
        const tabContents = document.querySelectorAll('.profile-tab-content');
        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.dataset.tab === tabName) {
                content.classList.add('active');
            }
        });
        
        // Анимация перехода
        const activeContent = document.querySelector(`[data-tab="${tabName}"]`);
        if (activeContent) {
            activeContent.style.opacity = '0';
            setTimeout(() => {
                activeContent.style.opacity = '1';
            }, 50);
        }
    }

    animateChecklist() {
        const checkItems = document.querySelectorAll('.profile-check-item');
        checkItems.forEach((item, index) => {
            setTimeout(() => {
                item.style.opacity = '0';
                item.style.transform = 'translateX(-20px)';
                item.style.transition = 'all 0.3s ease';
                
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateX(0)';
                }, 100);
            }, index * 200);
        });
    }

    showDeleteModal() {
        // Удаляем старое модальное окно, если оно есть
        const oldModal = document.getElementById('deleteAccountModal');
        if (oldModal) oldModal.remove();
        // Создаем модальное окно
        const modal = document.createElement('div');
        modal.id = 'deleteAccountModal';
        modal.innerHTML = `
            <div style="position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.32);z-index:9999;display:flex;align-items:center;justify-content:center;">
                <div style="background:#fff;padding:32px 20px 20px 20px;border-radius:18px;max-width:320px;width:90vw;box-shadow:0 4px 32px rgba(0,0,0,0.12);text-align:center;position:relative;">
                    <div style="font-size:20px;font-weight:700;margin-bottom:12px;">Удалить аккаунт?</div>
                    <div style="font-size:15px;color:#444;margin-bottom:24px;">Вы уверены, что хотите удалить свою запись? Это действие необратимо.</div>
                    <button id="confirmDeleteAccount" style="width:100%;padding:12px 0;background:#f65446;color:#fff;font-size:16px;font-weight:600;border:none;border-radius:10px;box-shadow:0 2px 8px rgba(246,84,70,0.08);margin-bottom:10px;">Удалить</button>
                    <button id="cancelDeleteAccount" style="width:100%;padding:12px 0;background:#F2F2F2;color:#222;font-size:16px;font-weight:500;border:none;border-radius:10px;">Отмена</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        document.getElementById('cancelDeleteAccount').onclick = () => modal.remove();
        document.getElementById('confirmDeleteAccount').onclick = () => this.deleteAccount();
    }

    async deleteAccount() {
        // Здесь должен быть реальный вызов API для удаления аккаунта
        // await api.deleteAccount();
        // Очищаем локальное состояние
        if (window.stateManager) window.stateManager.clearUserData && window.stateManager.clearUserData();
        // Удаляем модальное окно
        const modal = document.getElementById('deleteAccountModal');
        if (modal) modal.remove();
        // Перенаправляем на главный экран или авторизацию
        if (window.router) window.router.navigate && window.router.navigate('login');
        else window.location.reload();
    }
}

export default ProfileScreen; 