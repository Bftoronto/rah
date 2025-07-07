class RatingScreen {
    constructor() {
        this.currentPage = 1;
        this.currentTab = 'ratings';
        this.currentUserId = null;
    }

    async init(userId = null) {
        this.currentUserId = userId || app.state.currentUser?.id;
        if (!this.currentUserId) {
            app.showError('Пользователь не найден');
            return;
        }

        await this.render();
        this.bindEvents();
    }

    async render() {
        const container = document.getElementById('app');
        container.innerHTML = `
            <div class="rating-screen">
                <div class="rating-header">
                    <button class="back-btn" onclick="app.navigate('profile')">
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <h1>Рейтинги и отзывы</h1>
                </div>

                <div class="rating-summary" id="ratingSummary">
                    <div class="loading">Загрузка...</div>
                </div>

                <div class="rating-tabs">
                    <button class="tab-btn active" data-tab="ratings">
                        <i class="fas fa-star"></i>
                        Рейтинги
                    </button>
                    <button class="tab-btn" data-tab="reviews">
                        <i class="fas fa-comment"></i>
                        Отзывы
                    </button>
                </div>

                <div class="rating-content">
                    <div class="tab-content active" id="ratingsTab">
                        <div class="rating-stats" id="ratingStats"></div>
                        <div class="rating-list" id="ratingList"></div>
                        <div class="pagination" id="ratingPagination"></div>
                    </div>

                    <div class="tab-content" id="reviewsTab">
                        <div class="review-stats" id="reviewStats"></div>
                        <div class="review-list" id="reviewList"></div>
                        <div class="pagination" id="reviewPagination"></div>
                    </div>
                </div>
            </div>
        `;

        await this.loadSummary();
        await this.loadTabContent();
    }

    async loadSummary() {
        try {
            const response = await api.get(`/rating/user/${this.currentUserId}/summary`);
            const summary = response.data;

            const summaryHtml = `
                <div class="summary-grid">
                    <div class="summary-card">
                        <div class="summary-icon">
                            <i class="fas fa-star"></i>
                        </div>
                        <div class="summary-content">
                            <div class="summary-value">${summary.average_rating.toFixed(1)}</div>
                            <div class="summary-label">Средний рейтинг</div>
                            <div class="summary-sub">${summary.total_ratings} оценок</div>
                        </div>
                    </div>

                    <div class="summary-card">
                        <div class="summary-icon">
                            <i class="fas fa-comment"></i>
                        </div>
                        <div class="summary-content">
                            <div class="summary-value">${summary.total_reviews}</div>
                            <div class="summary-label">Всего отзывов</div>
                            <div class="summary-sub">${summary.positive_percentage}% положительных</div>
                        </div>
                    </div>

                    <div class="summary-card">
                        <div class="summary-icon">
                            <i class="fas fa-thumbs-up"></i>
                        </div>
                        <div class="summary-content">
                            <div class="summary-value">${summary.positive_reviews}</div>
                            <div class="summary-label">Положительных</div>
                            <div class="summary-sub">отзывов</div>
                        </div>
                    </div>

                    <div class="summary-card">
                        <div class="summary-icon">
                            <i class="fas fa-thumbs-down"></i>
                        </div>
                        <div class="summary-content">
                            <div class="summary-value">${summary.negative_reviews}</div>
                            <div class="summary-label">Отрицательных</div>
                            <div class="summary-sub">отзывов</div>
                        </div>
                    </div>
                </div>
            `;

            document.getElementById('ratingSummary').innerHTML = summaryHtml;
        } catch (error) {
            console.error('Ошибка загрузки сводки:', error);
            document.getElementById('ratingSummary').innerHTML = 
                '<div class="error">Ошибка загрузки данных</div>';
        }
    }

    async loadTabContent() {
        if (this.currentTab === 'ratings') {
            await this.loadRatings();
        } else {
            await this.loadReviews();
        }
    }

    async loadRatings(page = 1) {
        try {
            const response = await api.get(`/rating/user/${this.currentUserId}?page=${page}&limit=10`);
            const data = response.data;

            // Отображаем статистику рейтингов
            const statsHtml = `
                <div class="rating-distribution">
                    <h3>Распределение оценок</h3>
                    <div class="distribution-bars">
                        ${[5, 4, 3, 2, 1].map(stars => {
                            const count = data.rating_distribution[stars] || 0;
                            const percentage = data.total_ratings > 0 ? (count / data.total_ratings * 100) : 0;
                            return `
                                <div class="distribution-item">
                                    <div class="stars">${'★'.repeat(stars)}${'☆'.repeat(5-stars)}</div>
                                    <div class="bar-container">
                                        <div class="bar" style="width: ${percentage}%"></div>
                                    </div>
                                    <div class="count">${count}</div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
            document.getElementById('ratingStats').innerHTML = statsHtml;

            // Отображаем список рейтингов
            const ratingsHtml = data.ratings.map(rating => `
                <div class="rating-item">
                    <div class="rating-header">
                        <div class="rating-stars">
                            ${'★'.repeat(rating.rating)}${'☆'.repeat(5-rating.rating)}
                        </div>
                        <div class="rating-date">
                            ${new Date(rating.created_at).toLocaleDateString('ru-RU')}
                        </div>
                    </div>
                    ${rating.comment ? `<div class="rating-comment">${rating.comment}</div>` : ''}
                    <div class="rating-author">
                        <i class="fas fa-user"></i>
                        ${rating.from_user?.full_name || 'Пользователь'}
                    </div>
                </div>
            `).join('') || '<div class="empty-state">Пока нет оценок</div>';

            document.getElementById('ratingList').innerHTML = ratingsHtml;

            // Отображаем пагинацию
            this.renderPagination('ratingPagination', data.page, data.total_pages, (page) => {
                this.loadRatings(page);
            });

        } catch (error) {
            console.error('Ошибка загрузки рейтингов:', error);
            document.getElementById('ratingList').innerHTML = 
                '<div class="error">Ошибка загрузки рейтингов</div>';
        }
    }

    async loadReviews(page = 1) {
        try {
            const response = await api.get(`/rating/user/${this.currentUserId}/reviews?page=${page}&limit=10`);
            const data = response.data;

            // Отображаем статистику отзывов
            const statsHtml = `
                <div class="review-stats-summary">
                    <div class="stat-item">
                        <div class="stat-value positive">${data.positive_reviews}</div>
                        <div class="stat-label">Положительных</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value negative">${data.negative_reviews}</div>
                        <div class="stat-label">Отрицательных</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${data.positive_percentage}%</div>
                        <div class="stat-label">Положительных</div>
                    </div>
                </div>
            `;
            document.getElementById('reviewStats').innerHTML = statsHtml;

            // Отображаем список отзывов
            const reviewsHtml = data.reviews.map(review => `
                <div class="review-item ${review.is_positive ? 'positive' : 'negative'}">
                    <div class="review-header">
                        <div class="review-type">
                            <i class="fas fa-${review.is_positive ? 'thumbs-up' : 'thumbs-down'}"></i>
                            ${review.is_positive ? 'Положительный' : 'Отрицательный'}
                        </div>
                        <div class="review-date">
                            ${new Date(review.created_at).toLocaleDateString('ru-RU')}
                        </div>
                    </div>
                    <div class="review-text">${review.text}</div>
                    <div class="review-author">
                        <i class="fas fa-user"></i>
                        ${review.from_user?.full_name || 'Пользователь'}
                    </div>
                </div>
            `).join('') || '<div class="empty-state">Пока нет отзывов</div>';

            document.getElementById('reviewList').innerHTML = reviewsHtml;

            // Отображаем пагинацию
            this.renderPagination('reviewPagination', data.page, data.total_pages, (page) => {
                this.loadReviews(page);
            });

        } catch (error) {
            console.error('Ошибка загрузки отзывов:', error);
            document.getElementById('reviewList').innerHTML = 
                '<div class="error">Ошибка загрузки отзывов</div>';
        }
    }

    renderPagination(containerId, currentPage, totalPages, onPageChange) {
        const container = document.getElementById(containerId);
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let paginationHtml = '<div class="pagination-controls">';
        
        // Кнопка "Назад"
        if (currentPage > 1) {
            paginationHtml += `<button class="page-btn" onclick="(${onPageChange.toString()})(${currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>`;
        }

        // Номера страниц
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            paginationHtml += `<button class="page-btn ${i === currentPage ? 'active' : ''}" 
                onclick="(${onPageChange.toString()})(${i})">${i}</button>`;
        }

        // Кнопка "Вперед"
        if (currentPage < totalPages) {
            paginationHtml += `<button class="page-btn" onclick="(${onPageChange.toString()})(${currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>`;
        }

        paginationHtml += '</div>';
        container.innerHTML = paginationHtml;
    }

    bindEvents() {
        // Переключение вкладок
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.closest('.tab-btn').dataset.tab;
                this.switchTab(tab);
            });
        });
    }

    switchTab(tab) {
        // Обновляем активную вкладку
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tab}"]`).classList.add('active');

        // Обновляем контент
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tab}Tab`).classList.add('active');

        this.currentTab = tab;
        this.currentPage = 1;
        this.loadTabContent();
    }
}

// Экран для создания рейтинга
class CreateRatingScreen {
    constructor() {
        this.rideId = null;
        this.targetUserId = null;
        this.rating = 0;
        this.comment = '';
    }

    async init(rideId, targetUserId) {
        this.rideId = rideId;
        this.targetUserId = targetUserId;
        await this.render();
        this.bindEvents();
    }

    async render() {
        const container = document.getElementById('app');
        container.innerHTML = `
            <div class="create-rating-screen">
                <div class="rating-header">
                    <button class="back-btn" onclick="app.navigate('rideDetails', ${this.rideId})">
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <h1>Оценить поездку</h1>
                </div>

                <div class="rating-form">
                    <div class="rating-stars-container">
                        <h3>Ваша оценка</h3>
                        <div class="rating-stars" id="ratingStars">
                            <i class="fas fa-star" data-rating="1"></i>
                            <i class="fas fa-star" data-rating="2"></i>
                            <i class="fas fa-star" data-rating="3"></i>
                            <i class="fas fa-star" data-rating="4"></i>
                            <i class="fas fa-star" data-rating="5"></i>
                        </div>
                        <div class="rating-text" id="ratingText">Выберите оценку</div>
                    </div>

                    <div class="form-group">
                        <label for="ratingComment">Комментарий (необязательно)</label>
                        <textarea 
                            id="ratingComment" 
                            placeholder="Расскажите о поездке..."
                            maxlength="1000"
                        ></textarea>
                        <div class="char-count">
                            <span id="charCount">0</span>/1000
                        </div>
                    </div>

                    <div class="form-actions">
                        <button class="btn btn-secondary" onclick="app.navigate('rideDetails', ${this.rideId})">
                            Отмена
                        </button>
                        <button class="btn btn-primary" id="submitRating" disabled>
                            Отправить оценку
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Обработка звездочек
        document.querySelectorAll('#ratingStars i').forEach(star => {
            star.addEventListener('click', (e) => {
                const rating = parseInt(e.target.dataset.rating);
                this.setRating(rating);
            });

            star.addEventListener('mouseenter', (e) => {
                const rating = parseInt(e.target.dataset.rating);
                this.highlightStars(rating);
            });
        });

        document.getElementById('ratingStars').addEventListener('mouseleave', () => {
            this.highlightStars(this.rating);
        });

        // Обработка комментария
        const commentTextarea = document.getElementById('ratingComment');
        commentTextarea.addEventListener('input', (e) => {
            this.comment = e.target.value;
            this.updateCharCount();
            this.updateSubmitButton();
        });

        // Отправка рейтинга
        document.getElementById('submitRating').addEventListener('click', () => {
            this.submitRating();
        });
    }

    setRating(rating) {
        this.rating = rating;
        this.highlightStars(rating);
        this.updateRatingText();
        this.updateSubmitButton();
    }

    highlightStars(rating) {
        document.querySelectorAll('#ratingStars i').forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }

    updateRatingText() {
        const texts = {
            0: 'Выберите оценку',
            1: 'Ужасно',
            2: 'Плохо',
            3: 'Нормально',
            4: 'Хорошо',
            5: 'Отлично'
        };
        document.getElementById('ratingText').textContent = texts[this.rating];
    }

    updateCharCount() {
        const count = this.comment.length;
        document.getElementById('charCount').textContent = count;
    }

    updateSubmitButton() {
        const submitBtn = document.getElementById('submitRating');
        submitBtn.disabled = this.rating === 0;
    }

    async submitRating() {
        if (this.rating === 0) return;

        try {
            const submitBtn = document.getElementById('submitRating');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Отправка...';

            const ratingData = {
                target_user_id: this.targetUserId,
                ride_id: this.rideId,
                rating: this.rating,
                comment: this.comment.trim() || null
            };

            await api.post('/rating/', ratingData);

            app.showSuccess('Оценка успешно отправлена!');
            app.navigate('rideDetails', this.rideId);

        } catch (error) {
            console.error('Ошибка отправки рейтинга:', error);
            app.showError(error.response?.data?.detail || 'Ошибка отправки рейтинга');
            
            const submitBtn = document.getElementById('submitRating');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Отправить оценку';
        }
    }
}

// Экран для создания отзыва
class CreateReviewScreen {
    constructor() {
        this.rideId = null;
        this.targetUserId = null;
        this.text = '';
        this.isPositive = true;
    }

    async init(rideId, targetUserId) {
        this.rideId = rideId;
        this.targetUserId = targetUserId;
        await this.render();
        this.bindEvents();
    }

    async render() {
        const container = document.getElementById('app');
        container.innerHTML = `
            <div class="create-review-screen">
                <div class="review-header">
                    <button class="back-btn" onclick="app.navigate('rideDetails', ${this.rideId})">
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <h1>Оставить отзыв</h1>
                </div>

                <div class="review-form">
                    <div class="review-type-selector">
                        <h3>Тип отзыва</h3>
                        <div class="type-buttons">
                            <button class="type-btn active" data-type="positive">
                                <i class="fas fa-thumbs-up"></i>
                                Положительный
                            </button>
                            <button class="type-btn" data-type="negative">
                                <i class="fas fa-thumbs-down"></i>
                                Отрицательный
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="reviewText">Текст отзыва</label>
                        <textarea 
                            id="reviewText" 
                            placeholder="Расскажите о поездке подробнее..."
                            maxlength="2000"
                            required
                        ></textarea>
                        <div class="char-count">
                            <span id="charCount">0</span>/2000
                        </div>
                    </div>

                    <div class="form-actions">
                        <button class="btn btn-secondary" onclick="app.navigate('rideDetails', ${this.rideId})">
                            Отмена
                        </button>
                        <button class="btn btn-primary" id="submitReview" disabled>
                            Отправить отзыв
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Выбор типа отзыва
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setReviewType(e.target.closest('.type-btn').dataset.type);
            });
        });

        // Обработка текста отзыва
        const reviewTextarea = document.getElementById('reviewText');
        reviewTextarea.addEventListener('input', (e) => {
            this.text = e.target.value;
            this.updateCharCount();
            this.updateSubmitButton();
        });

        // Отправка отзыва
        document.getElementById('submitReview').addEventListener('click', () => {
            this.submitReview();
        });
    }

    setReviewType(type) {
        this.isPositive = type === 'positive';
        
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-type="${type}"]`).classList.add('active');
    }

    updateCharCount() {
        const count = this.text.length;
        document.getElementById('charCount').textContent = count;
    }

    updateSubmitButton() {
        const submitBtn = document.getElementById('submitReview');
        submitBtn.disabled = this.text.trim().length < 10;
    }

    async submitReview() {
        if (this.text.trim().length < 10) return;

        try {
            const submitBtn = document.getElementById('submitReview');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Отправка...';

            const reviewData = {
                target_user_id: this.targetUserId,
                ride_id: this.rideId,
                text: this.text.trim(),
                is_positive: this.isPositive
            };

            await api.post('/rating/review', reviewData);

            app.showSuccess('Отзыв успешно отправлен!');
            app.navigate('rideDetails', this.rideId);

        } catch (error) {
            console.error('Ошибка отправки отзыва:', error);
            app.showError(error.response?.data?.detail || 'Ошибка отправки отзыва');
            
            const submitBtn = document.getElementById('submitReview');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Отправить отзыв';
        }
    }
}

// Экспорт классов
window.RatingScreen = RatingScreen;
window.CreateRatingScreen = CreateRatingScreen;
window.CreateReviewScreen = CreateReviewScreen; 