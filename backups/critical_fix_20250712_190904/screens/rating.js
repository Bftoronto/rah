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
        
        // Безопасное создание HTML
        const ratingScreen = document.createElement('div');
        ratingScreen.className = 'rating-screen';
        
        const header = document.createElement('div');
        header.className = 'rating-header';
        
        const backBtn = document.createElement('button');
        backBtn.className = 'back-btn';
        backBtn.innerHTML = '<i class="fas fa-arrow-left"></i>';
        backBtn.addEventListener('click', () => app.navigate('profile'));
        
        const title = document.createElement('h1');
        title.textContent = 'Рейтинги и отзывы';
        
        header.appendChild(backBtn);
        header.appendChild(title);
        
        const summary = document.createElement('div');
        summary.className = 'rating-summary';
        summary.id = 'ratingSummary';
        
        const loading = document.createElement('div');
        loading.className = 'loading';
        loading.textContent = 'Загрузка...';
        summary.appendChild(loading);
        
        const tabs = document.createElement('div');
        tabs.className = 'rating-tabs';
        
        const ratingsTab = document.createElement('button');
        ratingsTab.className = 'tab-btn active';
        ratingsTab.setAttribute('data-tab', 'ratings');
        ratingsTab.innerHTML = '<i class="fas fa-star"></i> Рейтинги';
        
        const reviewsTab = document.createElement('button');
        reviewsTab.className = 'tab-btn';
        reviewsTab.setAttribute('data-tab', 'reviews');
        reviewsTab.innerHTML = '<i class="fas fa-comment"></i> Отзывы';
        
        tabs.appendChild(ratingsTab);
        tabs.appendChild(reviewsTab);
        
        const content = document.createElement('div');
        content.className = 'rating-content';
        
        const ratingsContent = document.createElement('div');
        ratingsContent.className = 'tab-content active';
        ratingsContent.id = 'ratingsTab';
        
        const ratingStats = document.createElement('div');
        ratingStats.className = 'rating-stats';
        ratingStats.id = 'ratingStats';
        
        const ratingList = document.createElement('div');
        ratingList.className = 'rating-list';
        ratingList.id = 'ratingList';
        
        const ratingPagination = document.createElement('div');
        ratingPagination.className = 'pagination';
        ratingPagination.id = 'ratingPagination';
        
        ratingsContent.appendChild(ratingStats);
        ratingsContent.appendChild(ratingList);
        ratingsContent.appendChild(ratingPagination);
        
        const reviewsContent = document.createElement('div');
        reviewsContent.className = 'tab-content';
        reviewsContent.id = 'reviewsTab';
        
        const reviewStats = document.createElement('div');
        reviewStats.className = 'review-stats';
        reviewStats.id = 'reviewStats';
        
        const reviewList = document.createElement('div');
        reviewList.className = 'review-list';
        reviewList.id = 'reviewList';
        
        const reviewPagination = document.createElement('div');
        reviewPagination.className = 'pagination';
        reviewPagination.id = 'reviewPagination';
        
        reviewsContent.appendChild(reviewStats);
        reviewsContent.appendChild(reviewList);
        reviewsContent.appendChild(reviewPagination);
        
        content.appendChild(ratingsContent);
        content.appendChild(reviewsContent);
        
        ratingScreen.appendChild(header);
        ratingScreen.appendChild(summary);
        ratingScreen.appendChild(tabs);
        ratingScreen.appendChild(content);
        
        // Очищаем контейнер и добавляем безопасный HTML
        container.innerHTML = '';
        container.appendChild(ratingScreen);

        await this.loadSummary();
        await this.loadTabContent();
    }

    async loadSummary() {
        try {
            const response = await api.get(`/rating/user/${this.currentUserId}/summary`);
            const summary = response.data;

            const summaryContainer = document.getElementById('ratingSummary');
            summaryContainer.innerHTML = '';
            
            const summaryGrid = document.createElement('div');
            summaryGrid.className = 'summary-grid';
            
            // Создаем карточки сводки безопасно
            const cards = [
                {
                    icon: 'fas fa-star',
                    value: summary.average_rating.toFixed(1),
                    label: 'Средний рейтинг',
                    sub: `${summary.total_ratings} оценок`
                },
                {
                    icon: 'fas fa-comment',
                    value: summary.total_reviews.toString(),
                    label: 'Всего отзывов',
                    sub: `${summary.positive_percentage}% положительных`
                },
                {
                    icon: 'fas fa-thumbs-up',
                    value: summary.positive_reviews.toString(),
                    label: 'Положительных',
                    sub: 'отзывов'
                },
                {
                    icon: 'fas fa-thumbs-down',
                    value: summary.negative_reviews.toString(),
                    label: 'Отрицательных',
                    sub: 'отзывов'
                }
            ];
            
            cards.forEach(card => {
                const cardElement = document.createElement('div');
                cardElement.className = 'summary-card';
                
                const icon = document.createElement('div');
                icon.className = 'summary-icon';
                icon.innerHTML = `<i class="${card.icon}"></i>`;
                
                const content = document.createElement('div');
                content.className = 'summary-content';
                
                const value = document.createElement('div');
                value.className = 'summary-value';
                value.textContent = card.value;
                
                const label = document.createElement('div');
                label.className = 'summary-label';
                label.textContent = card.label;
                
                const sub = document.createElement('div');
                sub.className = 'summary-sub';
                sub.textContent = card.sub;
                
                content.appendChild(value);
                content.appendChild(label);
                content.appendChild(sub);
                
                cardElement.appendChild(icon);
                cardElement.appendChild(content);
                summaryGrid.appendChild(cardElement);
            });
            
            summaryContainer.appendChild(summaryGrid);
        } catch (error) {
            console.error('Ошибка загрузки сводки:', error);
            const summaryContainer = document.getElementById('ratingSummary');
            summaryContainer.innerHTML = '';
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = 'Ошибка загрузки данных';
            summaryContainer.appendChild(errorDiv);
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

            // Отображаем статистику рейтингов безопасно
            const statsContainer = document.getElementById('ratingStats');
            statsContainer.innerHTML = '';
            
            const distribution = document.createElement('div');
            distribution.className = 'rating-distribution';
            
            const title = document.createElement('h3');
            title.textContent = 'Распределение оценок';
            
            const bars = document.createElement('div');
            bars.className = 'distribution-bars';
            
            [5, 4, 3, 2, 1].forEach(stars => {
                const count = data.rating_distribution[stars] || 0;
                const percentage = data.total_ratings > 0 ? (count / data.total_ratings * 100) : 0;
                
                const item = document.createElement('div');
                item.className = 'distribution-item';
                
                const starsElement = document.createElement('div');
                starsElement.className = 'stars';
                starsElement.textContent = '★'.repeat(stars) + '☆'.repeat(5-stars);
                
                const barContainer = document.createElement('div');
                barContainer.className = 'bar-container';
                
                const bar = document.createElement('div');
                bar.className = 'bar';
                bar.style.width = `${percentage}%`;
                
                const countElement = document.createElement('div');
                countElement.className = 'count';
                countElement.textContent = count.toString();
                
                barContainer.appendChild(bar);
                item.appendChild(starsElement);
                item.appendChild(barContainer);
                item.appendChild(countElement);
                bars.appendChild(item);
            });
            
            distribution.appendChild(title);
            distribution.appendChild(bars);
            statsContainer.appendChild(distribution);

            // Отображаем список рейтингов безопасно
            const listContainer = document.getElementById('ratingList');
            listContainer.innerHTML = '';
            
            if (data.ratings && data.ratings.length > 0) {
                data.ratings.forEach(rating => {
                    const item = document.createElement('div');
                    item.className = 'rating-item';
                    
                    const header = document.createElement('div');
                    header.className = 'rating-header';
                    
                    const stars = document.createElement('div');
                    stars.className = 'rating-stars';
                    stars.textContent = '★'.repeat(rating.rating) + '☆'.repeat(5-rating.rating);
                    
                    const date = document.createElement('div');
                    date.className = 'rating-date';
                    date.textContent = new Date(rating.created_at).toLocaleDateString('ru-RU');
                    
                    header.appendChild(stars);
                    header.appendChild(date);
                    item.appendChild(header);
                    
                    if (rating.comment) {
                        const comment = document.createElement('div');
                        comment.className = 'rating-comment';
                        comment.textContent = rating.comment;
                        item.appendChild(comment);
                    }
                    
                    const author = document.createElement('div');
                    author.className = 'rating-author';
                    author.innerHTML = '<i class="fas fa-user"></i>';
                    const authorName = document.createElement('span');
                    authorName.textContent = rating.from_user?.full_name || 'Пользователь';
                    author.appendChild(authorName);
                    item.appendChild(author);
                    
                    listContainer.appendChild(item);
                });
            } else {
                const emptyState = document.createElement('div');
                emptyState.className = 'empty-state';
                emptyState.textContent = 'Пока нет оценок';
                listContainer.appendChild(emptyState);
            }

            // Отображаем пагинацию
            this.renderPagination('ratingPagination', data.page, data.total_pages, (page) => {
                this.loadRatings(page);
            });

        } catch (error) {
            console.error('Ошибка загрузки рейтингов:', error);
            const listContainer = document.getElementById('ratingList');
            listContainer.innerHTML = '';
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = 'Ошибка загрузки рейтингов';
            listContainer.appendChild(errorDiv);
        }
    }

    async loadReviews(page = 1) {
        try {
            const response = await api.get(`/rating/user/${this.currentUserId}/reviews?page=${page}&limit=10`);
            const data = response.data;

            // Отображаем статистику отзывов безопасно
            const statsContainer = document.getElementById('reviewStats');
            statsContainer.innerHTML = '';
            
            const statsSummary = document.createElement('div');
            statsSummary.className = 'review-stats-summary';
            
            const stats = [
                { value: data.positive_reviews, label: 'Положительных', className: 'positive' },
                { value: data.negative_reviews, label: 'Отрицательных', className: 'negative' },
                { value: `${data.positive_percentage}%`, label: 'Положительных', className: '' }
            ];
            
            stats.forEach(stat => {
                const item = document.createElement('div');
                item.className = 'stat-item';
                
                const value = document.createElement('div');
                value.className = `stat-value ${stat.className}`;
                value.textContent = stat.value;
                
                const label = document.createElement('div');
                label.className = 'stat-label';
                label.textContent = stat.label;
                
                item.appendChild(value);
                item.appendChild(label);
                statsSummary.appendChild(item);
            });
            
            statsContainer.appendChild(statsSummary);

            // Отображаем список отзывов безопасно
            const listContainer = document.getElementById('reviewList');
            listContainer.innerHTML = '';
            
            if (data.reviews && data.reviews.length > 0) {
                data.reviews.forEach(review => {
                    const item = document.createElement('div');
                    item.className = `review-item ${review.is_positive ? 'positive' : 'negative'}`;
                    
                    const header = document.createElement('div');
                    header.className = 'review-header';
                    
                    const type = document.createElement('div');
                    type.className = 'review-type';
                    type.innerHTML = `<i class="fas fa-${review.is_positive ? 'thumbs-up' : 'thumbs-down'}"></i>`;
                    const typeText = document.createElement('span');
                    typeText.textContent = review.is_positive ? 'Положительный' : 'Отрицательный';
                    type.appendChild(typeText);
                    
                    const date = document.createElement('div');
                    date.className = 'review-date';
                    date.textContent = new Date(review.created_at).toLocaleDateString('ru-RU');
                    
                    header.appendChild(type);
                    header.appendChild(date);
                    item.appendChild(header);
                    
                    const text = document.createElement('div');
                    text.className = 'review-text';
                    text.textContent = review.text;
                    item.appendChild(text);
                    
                    const author = document.createElement('div');
                    author.className = 'review-author';
                    author.innerHTML = '<i class="fas fa-user"></i>';
                    const authorName = document.createElement('span');
                    authorName.textContent = review.from_user?.full_name || 'Пользователь';
                    author.appendChild(authorName);
                    item.appendChild(author);
                    
                    listContainer.appendChild(item);
                });
            } else {
                const emptyState = document.createElement('div');
                emptyState.className = 'empty-state';
                emptyState.textContent = 'Пока нет отзывов';
                listContainer.appendChild(emptyState);
            }

            // Отображаем пагинацию
            this.renderPagination('reviewPagination', data.page, data.total_pages, (page) => {
                this.loadReviews(page);
            });

        } catch (error) {
            console.error('Ошибка загрузки отзывов:', error);
            const listContainer = document.getElementById('reviewList');
            listContainer.innerHTML = '';
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = 'Ошибка загрузки отзывов';
            listContainer.appendChild(errorDiv);
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