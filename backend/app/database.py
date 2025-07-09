from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from .config_simple import settings
import logging
import time

logger = logging.getLogger(__name__)

# Создание движка базы данных с улучшенными настройками
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug,
    connect_args={
        "connect_timeout": 10,
        "application_name": "pax_backend"
    }
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
        from .models import user, ride, chat, upload, notification, moderation, rating
        
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
            
            conn.commit()
            logger.info("Индексы успешно созданы")
            
    except Exception as e:
        logger.error(f"Ошибка создания индексов: {e}")
        raise

def check_db_connection():
    """Проверка подключения к базе данных с retry логикой"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("Подключение к базе данных успешно")
            return True
        except OperationalError as e:
            logger.warning(f"Попытка {attempt + 1}/{max_retries} подключения к БД не удалась: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Повторная попытка через {retry_delay} секунды...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Экспоненциальная задержка
            else:
                logger.error(f"Все попытки подключения к БД исчерпаны. Последняя ошибка: {e}")
                return False
        except SQLAlchemyError as e:
            logger.error(f"Ошибка SQLAlchemy при подключении к БД: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при подключении к БД: {e}")
            return False 