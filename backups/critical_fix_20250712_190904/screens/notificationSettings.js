import Utils from '../utils.js';

class NotificationSettingsScreen {
    constructor() {
        this.settings = null;
    }

    async init() {
        await this.loadSettings();
        this.render();
        this.bindEvents();
    }

    async loadSettings() {
        try {
            const user = appState.getCurrentUser();
            if (!user) {
                appRouter.navigateTo('/login');
                return;
            }

            const response = await api.get(`/notifications/settings/${user.id}`);
            this.settings = response;
        } catch (error) {
            console.error('Ошибка загрузки настроек уведомлений:', error);
            this.showError('Не удалось загрузить настройки уведомлений');
        }
    }

    async saveSettings() {
        try {
            const user = appState.getCurrentUser();
            if (!user) return;

            const settingsData = {
                user_id: user.id,
                ride_notifications: document.getElementById('ride-notifications').checked,
                system_notifications: document.getElementById('system-notifications').checked,
                reminder_notifications: document.getElementById('reminder-notifications').checked,
                marketing_notifications: document.getElementById('marketing-notifications').checked,
                quiet_hours_start: document.getElementById('quiet-hours-start').value || null,
                quiet_hours_end: document.getElementById('quiet-hours-end').value || null
            };

            await api.put(`/notifications/settings/${user.id}`, settingsData);
            this.showSuccess('Настройки уведомлений сохранены');
        } catch (error) {
            console.error('Ошибка сохранения настроек:', error);
            this.showError('Не удалось сохранить настройки');
        }
    }

    async testNotification() {
        try {
            const user = appState.getCurrentUser();
            if (!user) return;

            await api.get(`/notifications/test/${user.id}`);
            this.showSuccess('Тестовое уведомление отправлено');
        } catch (error) {
            console.error('Ошибка отправки тестового уведомления:', error);
            this.showError('Не удалось отправить тестовое уведомление');
        }
    }

    render() {
        const container = document.getElementById('app');
        container.innerHTML = `
            <div class="screen notification-settings-screen">
                <div class="header">
                    <button class="back-button" onclick="appRouter.navigateTo('/profile')">
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <h1>Настройки уведомлений</h1>
                </div>

                <div class="content">
                    <div class="settings-section">
                        <h2>Типы уведомлений</h2>
                        
                        <div class="setting-item">
                            <div class="setting-info">
                                <label for="ride-notifications">Уведомления о поездках</label>
                                <p>Новые поездки, изменения, отмены</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" id="ride-notifications" 
                                       ${this.settings?.ride_notifications ? 'checked' : ''}>
                                <span class="slider"></span>
                            </label>
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <label for="system-notifications">Системные уведомления</label>
                                <p>Важные обновления и информация</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" id="system-notifications" 
                                       ${this.settings?.system_notifications ? 'checked' : ''}>
                                <span class="slider"></span>
                            </label>
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <label for="reminder-notifications">Напоминания о поездках</label>
                                <p>Напоминания за час до поездки</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" id="reminder-notifications" 
                                       ${this.settings?.reminder_notifications ? 'checked' : ''}>
                                <span class="slider"></span>
                            </label>
                        </div>

                        <div class="setting-item">
                            <div class="setting-info">
                                <label for="marketing-notifications">Маркетинговые уведомления</label>
                                <p>Акции, новости и предложения</p>
                            </div>
                            <label class="switch">
                                <input type="checkbox" id="marketing-notifications" 
                                       ${this.settings?.marketing_notifications ? 'checked' : ''}>
                                <span class="slider"></span>
                            </label>
                        </div>
                    </div>

                    <div class="settings-section">
                        <h2>Тихие часы</h2>
                        <p class="section-description">
                            В это время уведомления не будут отправляться (кроме критически важных)
                        </p>
                        
                        <div class="quiet-hours-container">
                            <div class="time-input-group">
                                <label for="quiet-hours-start">Начало</label>
                                <input type="time" id="quiet-hours-start" 
                                       value="${this.settings?.quiet_hours_start || ''}">
                            </div>
                            
                            <div class="time-input-group">
                                <label for="quiet-hours-end">Конец</label>
                                <input type="time" id="quiet-hours-end" 
                                       value="${this.settings?.quiet_hours_end || ''}">
                            </div>
                        </div>
                    </div>

                    <div class="settings-section">
                        <h2>Тестирование</h2>
                        <p class="section-description">
                            Отправьте тестовое уведомление для проверки настроек
                        </p>
                        
                        <button class="btn btn-secondary test-notification-btn" onclick="notificationSettingsScreen.testNotification()">
                            <i class="fas fa-bell"></i>
                            Отправить тестовое уведомление
                        </button>
                    </div>

                    <div class="action-buttons">
                        <button class="btn btn-primary save-settings-btn" onclick="notificationSettingsScreen.saveSettings()">
                            <i class="fas fa-save"></i>
                            Сохранить настройки
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Автосохранение при изменении настроек
        const checkboxes = document.querySelectorAll('.setting-item input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.saveSettings();
            });
        });

        // Автосохранение при изменении времени
        const timeInputs = document.querySelectorAll('input[type="time"]');
        timeInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.saveSettings();
            });
        });
    }

    showSuccess(message) {
        Utils.showNotification('Успех', message, 'success');
    }

    showError(message) {
        Utils.showNotification('Ошибка', message, 'error');
    }
}

export default NotificationSettingsScreen;