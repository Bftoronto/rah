-- Миграция 005: Удаление платежных таблиц и компонентов
-- Дата: 2024-01-15

-- Удаление триггеров платежей
DROP TRIGGER IF EXISTS trigger_update_payment_counters ON payments;

-- Удаление функции обновления счетчиков платежей
DROP FUNCTION IF EXISTS update_payment_counters();

-- Удаление функции статистики платежей
DROP FUNCTION IF EXISTS get_payment_statistics(INTEGER);

-- Удаление индексов платежей
DROP INDEX IF EXISTS idx_payments_user_id;
DROP INDEX IF EXISTS idx_payments_ride_id;
DROP INDEX IF EXISTS idx_payments_status;
DROP INDEX IF EXISTS idx_payments_created_at;

-- Удаление таблицы платежей
DROP TABLE IF EXISTS payments CASCADE;

-- Удаление колонок счетчиков платежей из таблицы rides
ALTER TABLE rides DROP COLUMN IF EXISTS payments_count;

-- Удаление колонок счетчиков платежей из таблицы users
ALTER TABLE users DROP COLUMN IF EXISTS payments_count;

-- Обновление версии миграции
INSERT INTO migration_log (version, applied_at, description) 
VALUES ('005', CURRENT_TIMESTAMP, 'Удалены все платежные таблицы и компоненты')
ON CONFLICT (version) DO NOTHING; 