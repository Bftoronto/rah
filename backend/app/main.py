from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
import sys

from .config import settings
from .database import init_db, check_db_connection
from .api import auth, rides, profile, chat, payment, upload, notifications, moderation, rating

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=settings.log_file
)

logger = logging.getLogger(__name__)

# Создание приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug
)

# Настройка CORS для Telegram Web App
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://web.telegram.org",
        "https://t.me",
        "https://web.telegram.org",
        "https://t.me",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:3000",
        "https://localhost:8000",
        "https://rah.pages.dev",
        "https://pax-backend-2gng.onrender.com"
    ] + settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(rides.router, prefix="/api/rides", tags=["rides"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(payment.router, prefix="/api/payment", tags=["payment"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(moderation.router, prefix="/api/moderation", tags=["moderation"])
app.include_router(rating.router, prefix="/api/rating", tags=["rating"])

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    logger.info("Запуск приложения...")
    
    try:
        # Проверка подключения к базе данных
        if not check_db_connection():
            logger.error("Не удалось подключиться к базе данных")
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Инициализация базы данных
        init_db()
        logger.info("База данных инициализирована")
        
        logger.info("Приложение успешно запущено")
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)

@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения"""
    logger.info("Остановка приложения...")
    
    try:
        # Закрытие сессии уведомлений
        from .services.notification_service import notification_service
        await notification_service.close_session()
        logger.info("Сессия уведомлений закрыта")
    except Exception as e:
        logger.error(f"Ошибка закрытия сессии уведомлений: {e}")

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": f"Добро пожаловать в {settings.app_name}",
        "version": settings.version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    try:
        db_status = check_db_connection()
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "version": settings.version
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": settings.version
        }

@app.get("/api/info")
async def api_info():
    """Информация об API"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug,
        "endpoints": {
            "auth": "/api/auth",
            "rides": "/api/rides",
            "profile": "/api/profile",
            "chat": "/api/chat",
            "payment": "/api/payment",
            "upload": "/api/upload",
            "notifications": "/api/notifications",
            "moderation": "/api/moderation",
            "rating": "/api/rating"
        }
    } 