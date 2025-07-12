import Utils from '../utils.js';

class ReportScreen {
    constructor() {
        this.targetType = null;
        this.targetId = null;
        this.targetData = null;
    }

    async init(targetType, targetId) {
        this.targetType = targetType;
        this.targetId = targetId;
        await this.loadTargetData();
        this.render();
        this.bindEvents();
    }

    async loadTargetData() {
        try {
            if (this.targetType === 'user') {
                const response = await api.get(`/users/${this.targetId}`);
                this.targetData = response;
            } else if (this.targetType === 'ride') {
                const response = await api.get(`/rides/${this.targetId}`);
                this.targetData = response;
            }
        } catch (error) {
            console.error('Ошибка загрузки данных цели:', error);
            this.showError('Не удалось загрузить данные');
        }
    }

    async submitReport() {
        try {
            const reason = document.getElementById('report-reason').value;
            const description = document.getElementById('report-description').value;

            if (!reason) {
                this.showError('Выберите причину жалобы');
                return;
            }

            const reportData = {
                target_type: this.targetType,
                target_id: this.targetId,
                reason: reason,
                description: description || null
            };

            await api.post('/moderation/report', reportData);
            this.showSuccess('Жалоба отправлена');
            
            // Возвращаемся назад
            setTimeout(() => {
                window.history.back();
            }, 1500);

        } catch (error) {
            console.error('Ошибка отправки жалобы:', error);
            this.showError('Не удалось отправить жалобу');
        }
    }

    render() {
        const container = document.getElementById('app');
        
        let targetInfo = '';
        if (this.targetData) {
            if (this.targetType === 'user') {
                targetInfo = `
                    <div class="target-info">
                        <div class="target-avatar">
                            ${this.targetData.avatar ? 
                                `<img src="${this.targetData.avatar}" alt="Аватар">` : 
                                `<span>${this.targetData.full_name?.split(' ').map(n => n[0]).join('') || 'U'}</span>`
                            }
                        </div>
                        <div class="target-details">
                            <h3>${this.targetData.full_name || 'Пользователь'}</h3>
                            <p>${this.targetData.city || 'Город не указан'}</p>
                        </div>
                    </div>
                `;
            } else if (this.targetType === 'ride') {
                targetInfo = `
                    <div class="target-info">
                        <div class="target-icon">
                            <i class="fas fa-car"></i>
                        </div>
                        <div class="target-details">
                            <h3>Поездка</h3>
                            <p>${this.targetData.from_location || ''} → ${this.targetData.to_location || ''}</p>
                            <p>${this.targetData.date || ''} в ${this.targetData.time || ''}</p>
                        </div>
                    </div>
                `;
            }
        }

        container.innerHTML = `
            <div class="screen report-screen">
                <div class="header">
                    <button class="back-button" onclick="window.history.back()">
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <h1>Подать жалобу</h1>
                </div>

                <div class="content">
                    ${targetInfo}

                    <div class="report-form">
                        <div class="form-group">
                            <label for="report-reason">Причина жалобы *</label>
                            <select id="report-reason" class="form-control" required>
                                <option value="">Выберите причину</option>
                                <option value="spam">Спам</option>
                                <option value="inappropriate">Неприемлемый контент</option>
                                <option value="fraud">Мошенничество</option>
                                <option value="harassment">Домогательства</option>
                                <option value="fake">Фальшивая информация</option>
                                <option value="other">Другое</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="report-description">Описание (необязательно)</label>
                            <textarea id="report-description" class="form-control" 
                                      placeholder="Опишите подробнее причину жалобы..." 
                                      rows="4"></textarea>
                        </div>

                        <div class="report-guidelines">
                            <h3>Правила подачи жалоб:</h3>
                            <ul>
                                <li>Жалобы должны быть обоснованными</li>
                                <li>Не подавайте жалобы из мести</li>
                                <li>Опишите конкретную проблему</li>
                                <li>Ложные жалобы могут привести к блокировке</li>
                            </ul>
                        </div>

                        <div class="action-buttons">
                            <button class="btn btn-secondary cancel-btn" onclick="window.history.back()">
                                Отмена
                            </button>
                            <button class="btn btn-primary submit-btn" onclick="reportScreen.submitReport()">
                                <i class="fas fa-paper-plane"></i>
                                Отправить жалобу
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Обработка изменения причины жалобы
        const reasonSelect = document.getElementById('report-reason');
        if (reasonSelect) {
            reasonSelect.addEventListener('change', () => {
                this.updateDescriptionPlaceholder();
            });
        }

        // Обработка отправки формы по Enter
        const descriptionTextarea = document.getElementById('report-description');
        if (descriptionTextarea) {
            descriptionTextarea.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.submitReport();
                }
            });
        }
    }

    updateDescriptionPlaceholder() {
        const reason = document.getElementById('report-reason').value;
        const descriptionTextarea = document.getElementById('report-description');
        
        const placeholders = {
            'spam': 'Опишите, какой именно спам вы обнаружили...',
            'inappropriate': 'Опишите, какой контент является неприемлемым...',
            'fraud': 'Опишите признаки мошенничества...',
            'harassment': 'Опишите случаи домогательств...',
            'fake': 'Опишите, какая информация является фальшивой...',
            'other': 'Опишите проблему подробнее...'
        };
        
        if (descriptionTextarea) {
            descriptionTextarea.placeholder = placeholders[reason] || 'Опишите подробнее причину жалобы...';
        }
    }

    showSuccess(message) {
        Utils.showNotification('Успех', message, 'success');
    }

    showError(message) {
        Utils.showNotification('Ошибка', message, 'error');
    }
}

export default ReportScreen; 