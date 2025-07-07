-- Миграция для добавления индексов в таблицу пользователей
-- Улучшает производительность запросов

-- Индекс для поиска по городу
CREATE INDEX IF NOT EXISTS idx_user_city ON users(city);

-- Индекс для возрастных ограничений
CREATE INDEX IF NOT EXISTS idx_user_birth_date ON users(birth_date);

-- Индекс для проверки водительских прав
CREATE INDEX IF NOT EXISTS idx_user_driver_license ON users(driver_license_number);

-- Индекс для поиска по автомобилю
CREATE INDEX IF NOT EXISTS idx_user_car_info ON users(car_brand, car_model);

-- Индекс для отслеживания изменений
CREATE INDEX IF NOT EXISTS idx_user_updated ON users(updated_at);

-- Индекс для рейтингов
CREATE INDEX IF NOT EXISTS idx_user_rating_reviews ON users(average_rating, reviews);

-- Комментарий к миграции
COMMENT ON INDEX idx_user_city IS 'Индекс для поиска пользователей по городу';
COMMENT ON INDEX idx_user_birth_date IS 'Индекс для возрастных ограничений';
COMMENT ON INDEX idx_user_driver_license IS 'Индекс для проверки водительских прав';
COMMENT ON INDEX idx_user_car_info IS 'Индекс для поиска по автомобилю';
COMMENT ON INDEX idx_user_updated IS 'Индекс для отслеживания изменений профиля';
COMMENT ON INDEX idx_user_rating_reviews IS 'Индекс для рейтингов и отзывов'; 