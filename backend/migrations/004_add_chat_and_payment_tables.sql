-- Миграция 004: Добавление таблиц чата и платежей
-- Дата: 2024-01-15

-- Создание таблицы чатов
CREATE TABLE IF NOT EXISTS chats (
    id SERIAL PRIMARY KEY,
    ride_id INTEGER NOT NULL REFERENCES rides(id) ON DELETE CASCADE,
    user1_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user2_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ride_id, user1_id, user2_id)
);

-- Создание таблицы сообщений чата
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    user_from_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_to_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы платежей
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ride_id INTEGER NOT NULL REFERENCES rides(id) ON DELETE CASCADE,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_chats_ride_id ON chats(ride_id);
CREATE INDEX IF NOT EXISTS idx_chats_user1_id ON chats(user1_id);
CREATE INDEX IF NOT EXISTS idx_chats_user2_id ON chats(user2_id);
CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON chats(updated_at);

CREATE INDEX IF NOT EXISTS idx_chat_messages_chat_id ON chat_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_from_id ON chat_messages(user_from_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_to_id ON chat_messages(user_to_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_chat_messages_is_read ON chat_messages(is_read);

CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_ride_id ON payments(ride_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);

-- Добавление связей в таблицу rides
ALTER TABLE rides ADD COLUMN IF NOT EXISTS chats_count INTEGER DEFAULT 0;
ALTER TABLE rides ADD COLUMN IF NOT EXISTS payments_count INTEGER DEFAULT 0;

-- Добавление связей в таблицу users
ALTER TABLE users ADD COLUMN IF NOT EXISTS chats_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS messages_count INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS payments_count INTEGER DEFAULT 0;

-- Создание триггеров для обновления счетчиков
CREATE OR REPLACE FUNCTION update_chat_counters()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Увеличиваем счетчик чатов для пользователей
        UPDATE users SET chats_count = chats_count + 1 WHERE id = NEW.user1_id;
        UPDATE users SET chats_count = chats_count + 1 WHERE id = NEW.user2_id;
        -- Увеличиваем счетчик чатов для поездки
        UPDATE rides SET chats_count = chats_count + 1 WHERE id = NEW.ride_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Уменьшаем счетчик чатов для пользователей
        UPDATE users SET chats_count = chats_count - 1 WHERE id = OLD.user1_id;
        UPDATE users SET chats_count = chats_count - 1 WHERE id = OLD.user2_id;
        -- Уменьшаем счетчик чатов для поездки
        UPDATE rides SET chats_count = chats_count - 1 WHERE id = OLD.ride_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_message_counters()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Увеличиваем счетчик сообщений для отправителя
        UPDATE users SET messages_count = messages_count + 1 WHERE id = NEW.user_from_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Уменьшаем счетчик сообщений для отправителя
        UPDATE users SET messages_count = messages_count - 1 WHERE id = OLD.user_from_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_payment_counters()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Увеличиваем счетчик платежей для пользователя
        UPDATE users SET payments_count = payments_count + 1 WHERE id = NEW.user_id;
        -- Увеличиваем счетчик платежей для поездки
        UPDATE rides SET payments_count = payments_count + 1 WHERE id = NEW.ride_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Уменьшаем счетчик платежей для пользователя
        UPDATE users SET payments_count = payments_count - 1 WHERE id = OLD.user_id;
        -- Уменьшаем счетчик платежей для поездки
        UPDATE rides SET payments_count = payments_count - 1 WHERE id = OLD.ride_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Создание триггеров
DROP TRIGGER IF EXISTS trigger_update_chat_counters ON chats;
CREATE TRIGGER trigger_update_chat_counters
    AFTER INSERT OR DELETE ON chats
    FOR EACH ROW EXECUTE FUNCTION update_chat_counters();

DROP TRIGGER IF EXISTS trigger_update_message_counters ON chat_messages;
CREATE TRIGGER trigger_update_message_counters
    AFTER INSERT OR DELETE ON chat_messages
    FOR EACH ROW EXECUTE FUNCTION update_message_counters();

DROP TRIGGER IF EXISTS trigger_update_payment_counters ON payments;
CREATE TRIGGER trigger_update_payment_counters
    AFTER INSERT OR DELETE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_payment_counters();

-- Создание функции для очистки старых сообщений
CREATE OR REPLACE FUNCTION cleanup_old_messages(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM chat_messages 
    WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_old;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Создание функции для получения статистики чатов
CREATE OR REPLACE FUNCTION get_chat_statistics(user_id_param INTEGER)
RETURNS TABLE(
    total_chats INTEGER,
    total_messages INTEGER,
    unread_messages INTEGER,
    active_chats INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT c.id)::INTEGER as total_chats,
        COUNT(cm.id)::INTEGER as total_messages,
        COUNT(CASE WHEN cm.is_read = FALSE AND cm.user_to_id = user_id_param THEN 1 END)::INTEGER as unread_messages,
        COUNT(DISTINCT CASE WHEN cm.timestamp >= CURRENT_TIMESTAMP - INTERVAL '7 days' THEN c.id END)::INTEGER as active_chats
    FROM chats c
    LEFT JOIN chat_messages cm ON c.id = cm.chat_id
    WHERE c.user1_id = user_id_param OR c.user2_id = user_id_param;
END;
$$ LANGUAGE plpgsql;

-- Создание функции для получения статистики платежей
CREATE OR REPLACE FUNCTION get_payment_statistics(user_id_param INTEGER)
RETURNS TABLE(
    total_payments INTEGER,
    total_amount DECIMAL(10,2),
    refunded_amount DECIMAL(10,2),
    completed_payments INTEGER,
    refunded_payments INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_payments,
        COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as total_amount,
        COALESCE(SUM(CASE WHEN status = 'refunded' THEN amount ELSE 0 END), 0) as refunded_amount,
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::INTEGER as completed_payments,
        COUNT(CASE WHEN status = 'refunded' THEN 1 END)::INTEGER as refunded_payments
    FROM payments
    WHERE user_id = user_id_param;
END;
$$ LANGUAGE plpgsql;

-- Обновление версии миграции
INSERT INTO migration_log (version, applied_at, description) 
VALUES ('004', CURRENT_TIMESTAMP, 'Добавлены таблицы чата и платежей с индексами и триггерами')
ON CONFLICT (version) DO NOTHING; 