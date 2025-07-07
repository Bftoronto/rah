from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Создание движка базы данных
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Инициализация базы данных"""
    try:
        # Импорт всех моделей для создания таблиц
        from .models import user, ride, chat, payment, upload, notification, moderation, rating
        
        # Создание всех таблиц
        Base.metadata.create_all(bind=engine)
        logger.info("База данных успешно инициализирована")
        
        # Проверка и создание индексов
        create_indexes()
        
    except Exception as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
        raise

def create_indexes():
    """Создание дополнительных индексов для оптимизации"""
    try:
        with engine.connect() as conn:
            # Индексы для поездок
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rides_driver_id ON rides(driver_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rides_passenger_id ON rides(passenger_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rides_status ON rides(status)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rides_date ON rides(date)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rides_from_location ON rides(from_location)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rides_to_location ON rides(to_location)"))
            
            # Индексы для пользователей
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_is_driver ON users(is_driver)"))
            
            # Индексы для чатов
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chats_ride_id ON chats(ride_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chats_user1_id ON chats(user1_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chats_user2_id ON chats(user2_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON chats(updated_at)"))
            
            # Индексы для сообщений чата
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_messages_chat_id ON chat_messages(chat_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_messages_user_from_id ON chat_messages(user_from_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_messages_user_to_id ON chat_messages(user_to_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_chat_messages_is_read ON chat_messages(is_read)"))
            
            # Индексы для платежей
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payments_ride_id ON payments(ride_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at)"))
            
            conn.commit()
            logger.info("Индексы успешно созданы")
            
    except Exception as e:
        logger.error(f"Ошибка создания индексов: {e}")
        raise

def check_db_connection():
    """Проверка подключения к базе данных"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Подключение к базе данных успешно")
        return True
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return False 