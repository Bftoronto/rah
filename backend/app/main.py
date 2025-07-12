from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
import sys
import time

from .config.settings import get_settings, settings
from .database import init_db, check_db_connection
from .api import auth, rides, profile, chat, upload, notifications, moderation, rating, monitoring, cache
from .middleware.performance import PerformanceMiddleware, MemoryMonitor
from .middleware.rate_limit import rate_limit_middleware
from .utils.logger import get_logger, performance_logger
from .monitoring.metrics import metrics_collector, api_metrics

# Настройка логирования с использованием новой системы
logger = get_logger("main")

# Создание приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Добавляем middleware производительности
app.add_middleware(PerformanceMiddleware)

# Добавляем rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Настройка CORS для Telegram Web App
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "https://web.telegram.org",
        "https://t.me",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://localhost:3000",
        "https://localhost:8000",
        "https://frabjous-florentine-c506b0.netlify.app",
        "https://pax-backend-2gng.onrender.com"
    ] + settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Health check эндпоинт для keep-alive
@app.get("/health")
async def health_check():
    """Health check эндпоинт для мониторинга и keep-alive"""
    try:
        # Проверка подключения к базе данных
        db_status = check_db_connection()
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "timestamp": time.time(),
            "database": "connected" if db_status else "disconnected",
            "version": settings.version,
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e),
            "version": settings.version,
            "environment": settings.environment
        }

# Подключение роутеров
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(rides.router, prefix="/api/rides", tags=["rides"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(moderation.router, prefix="/api/moderation", tags=["moderation"])
app.include_router(rating.router, prefix="/api/rating", tags=["rating"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])

# Подключение кэш API
app.include_router(cache.router, prefix="/api/cache", tags=["cache"])

@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения с улучшенным логированием"""
    start_time = time.time()
    
    logger.info("Запуск приложения...", {
        "app_name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug
    })
    
    try:
        # Логируем использование памяти при запуске
        MemoryMonitor.log_memory_usage("startup")
        
        # Проверка подключения к базе данных
        logger.info("Проверка подключения к базе данных...")
        if not check_db_connection():
            logger.error("Не удалось подключиться к базе данных", {
                "database_url": settings.database_url.split("@")[0] + "@***" if "@" in settings.database_url else "***"
            })
            logger.warning("Приложение запускается без подключения к БД - некоторые функции могут быть недоступны")
            # НЕ ВЫХОДИМ ИЗ ПРИЛОЖЕНИЯ - позволяем ему запуститься
            return
        
        logger.info("Подключение к базе данных успешно")
        
        # Инициализация базы данных
        logger.info("Инициализация базы данных...")
        init_db()
        logger.info("База данных инициализирована")
        
        # Логируем время запуска
        startup_duration = (time.time() - start_time) * 1000
        performance_logger.api_request(
            endpoint="startup",
            method="STARTUP",
            duration_ms=startup_duration,
            status_code=200
        )
        
        logger.info("Приложение успешно запущено", {
            "startup_time_ms": startup_duration,
            "memory_usage_mb": MemoryMonitor.get_memory_usage()
        })
        
    except Exception as e:
        startup_duration = (time.time() - start_time) * 1000
        logger.error("Критическая ошибка при запуске", {
            "error": str(e),
            "startup_time_ms": startup_duration
        })
        logger.warning("Приложение запускается с ошибками - некоторые функции могут быть недоступны")
        # НЕ ВЫХОДИМ ИЗ ПРИЛОЖЕНИЯ - позволяем ему запуститься

@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения с улучшенным логированием"""
    logger.info("Остановка приложения...")
    
    try:
        # Логируем использование памяти при остановке
        MemoryMonitor.log_memory_usage("shutdown")
        
        # Закрытие сессии уведомлений
        from .services.notification_service import notification_service
        await notification_service.close_session()
        logger.info("Сессия уведомлений закрыта")
        
        logger.info("Приложение успешно остановлено")
        
    except Exception as e:
        logger.error("Ошибка при остановке приложения", {"error": str(e)})

@app.get("/")
async def root():
    """Корневой эндпоинт с информацией о системе"""
    return {
        "message": f"Добро пожаловать в {settings.app_name}",
        "version": settings.version,
        "status": "running",
        "timestamp": time.time(),
        "memory_usage_mb": round(MemoryMonitor.get_memory_usage(), 2)
    }

@app.get("/api/info")
async def api_info():
    """Информация об API с детальной статистикой"""
    return {
        "name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug,
        "timestamp": time.time(),
        "memory_usage_mb": round(MemoryMonitor.get_memory_usage(), 2),
        "endpoints": {
            "auth": "/api/auth",
            "rides": "/api/rides",
            "profile": "/api/profile",
            "chat": "/api/chat",
            "upload": "/api/upload",
            "notifications": "/api/notifications",
            "moderation": "/api/moderation",
            "rating": "/api/rating"
        },
        "features": {
            "telegram_integration": True,
            "file_upload": True,
            "real_time_notifications": True,
            "rating_system": True,
            "moderation_system": True,
            "performance_monitoring": True,
            "structured_logging": True
        }
    }

@app.get("/api/metrics")
async def get_metrics():
    """Метрики производительности приложения"""
    try:
        memory_usage = MemoryMonitor.get_memory_usage()
        
        # Получаем информацию о системе
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            disk_usage = psutil.disk_usage('/')
            
            return {
                "timestamp": time.time(),
                "memory": {
                    "usage_mb": round(memory_usage, 2),
                    "available_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2)
                },
                "cpu": {
                    "usage_percent": cpu_percent
                },
                "disk": {
                    "total_gb": round(disk_usage.total / 1024 / 1024 / 1024, 2),
                    "used_gb": round(disk_usage.used / 1024 / 1024 / 1024, 2),
                    "free_gb": round(disk_usage.free / 1024 / 1024 / 1024, 2)
                },
                "app": {
                    "version": settings.version,
                    "debug": settings.debug
                }
            }
        except ImportError:
            # Если psutil недоступен, возвращаем базовую информацию
            return {
                "timestamp": time.time(),
                "memory": {
                    "usage_mb": round(memory_usage, 2),
                    "available_mb": 0
                },
                "cpu": {
                    "usage_percent": 0
                },
                "disk": {
                    "total_gb": 0,
                    "used_gb": 0,
                    "free_gb": 0
                },
                "app": {
                    "version": settings.version,
                    "debug": settings.debug
                },
                "note": "psutil not available - limited metrics"
            }
        
    except Exception as e:
        logger.error("Ошибка получения метрик", {"error": str(e)})
        raise HTTPException(status_code=500, detail="Ошибка получения метрик") 