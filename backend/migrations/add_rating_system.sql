-- Миграция для добавления системы рейтингов и отзывов
-- Дата: 2024-01-XX

-- Добавление поля average_rating в таблицу users
ALTER TABLE users ADD COLUMN average_rating FLOAT DEFAULT 0.0;

-- Добавление полей в таблицу rides
ALTER TABLE rides ADD COLUMN passenger_id INTEGER REFERENCES users(id);
ALTER TABLE rides ADD COLUMN status VARCHAR(20) DEFAULT 'active';
ALTER TABLE rides ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Создание таблицы рейтингов
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ride_id INTEGER NOT NULL REFERENCES rides(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы отзывов
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ride_id INTEGER NOT NULL REFERENCES rides(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    is_positive BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации запросов
CREATE INDEX idx_rating_from_user ON ratings(from_user_id);
CREATE INDEX idx_rating_target_user ON ratings(target_user_id);
CREATE INDEX idx_rating_ride ON ratings(ride_id);
CREATE INDEX idx_rating_created ON ratings(created_at);

CREATE INDEX idx_review_from_user ON reviews(from_user_id);
CREATE INDEX idx_review_target_user ON reviews(target_user_id);
CREATE INDEX idx_review_ride ON reviews(ride_id);
CREATE INDEX idx_review_positive ON reviews(is_positive);
CREATE INDEX idx_review_created ON reviews(created_at);

-- Создание уникальных ограничений для предотвращения дублирования
CREATE UNIQUE INDEX idx_unique_rating ON ratings(from_user_id, target_user_id, ride_id);
CREATE UNIQUE INDEX idx_unique_review ON reviews(from_user_id, target_user_id, ride_id);

-- Создание триггера для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_ratings_updated_at BEFORE UPDATE ON ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Создание функции для обновления среднего рейтинга пользователя
CREATE OR REPLACE FUNCTION update_user_average_rating()
RETURNS TRIGGER AS $$
BEGIN
    -- Обновляем средний рейтинг пользователя
    UPDATE users 
    SET average_rating = (
        SELECT COALESCE(AVG(rating), 0.0)
        FROM ratings 
        WHERE target_user_id = COALESCE(NEW.target_user_id, OLD.target_user_id)
    )
    WHERE id = COALESCE(NEW.target_user_id, OLD.target_user_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Создание триггеров для автоматического обновления среднего рейтинга
CREATE TRIGGER update_user_rating_on_insert AFTER INSERT ON ratings
    FOR EACH ROW EXECUTE FUNCTION update_user_average_rating();

CREATE TRIGGER update_user_rating_on_update AFTER UPDATE ON ratings
    FOR EACH ROW EXECUTE FUNCTION update_user_average_rating();

CREATE TRIGGER update_user_rating_on_delete AFTER DELETE ON ratings
    FOR EACH ROW EXECUTE FUNCTION update_user_average_rating();

-- Добавление комментариев к таблицам
COMMENT ON TABLE ratings IS 'Таблица рейтингов пользователей';
COMMENT ON TABLE reviews IS 'Таблица отзывов пользователей';
COMMENT ON COLUMN ratings.rating IS 'Рейтинг от 1 до 5 звезд';
COMMENT ON COLUMN reviews.is_positive IS 'Положительный или отрицательный отзыв'; 