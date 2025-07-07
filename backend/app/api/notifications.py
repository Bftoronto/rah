from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from ..database import get_db
from ..services.notification_service import notification_service
from ..models.user import User
from ..schemas.notification import (
    NotificationCreate, 
    NotificationResponse, 
    BulkNotificationCreate,
    NotificationSettings
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/send/ride")
async def send_ride_notification(
    notification_data: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Отправка уведомления о поездке"""
    try:
        # Получаем пользователя
        user = db.query(User).filter(User.id == notification_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Отправляем уведомление в фоновом режиме
        background_tasks.add_task(
            notification_service.send_ride_notification,
            user=user,
            ride_data=notification_data.ride_data,
            notification_type=notification_data.notification_type,
            db=db
        )
        
        return {
            "success": True,
            "message": "Уведомление поставлено в очередь"
        }
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о поездке: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка отправки уведомления"
        )

@router.post("/send/system")
async def send_system_notification(
    notification_data: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Отправка системного уведомления"""
    try:
        # Получаем пользователя
        user = db.query(User).filter(User.id == notification_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Отправляем уведомление в фоновом режиме
        background_tasks.add_task(
            notification_service.send_system_notification,
            user=user,
            title=notification_data.title,
            message=notification_data.message,
            notification_type=notification_data.notification_type,
            db=db
        )
        
        return {
            "success": True,
            "message": "Системное уведомление поставлено в очередь"
        }
        
    except Exception as e:
        logger.error(f"Ошибка отправки системного уведомления: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка отправки уведомления"
        )

@router.post("/send/bulk")
async def send_bulk_notification(
    notification_data: BulkNotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Массовая рассылка уведомлений"""
    try:
        # Получаем пользователей
        users = db.query(User).filter(User.id.in_(notification_data.user_ids)).all()
        
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователи не найдены"
            )
        
        # Отправляем уведомления в фоновом режиме
        background_tasks.add_task(
            notification_service.send_bulk_notification,
            users=users,
            title=notification_data.title,
            message=notification_data.message,
            notification_type=notification_data.notification_type,
            db=db
        )
        
        return {
            "success": True,
            "message": f"Массовая рассылка поставлена в очередь для {len(users)} пользователей"
        }
        
    except Exception as e:
        logger.error(f"Ошибка массовой рассылки: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка массовой рассылки"
        )

@router.post("/reminders/send")
async def send_reminder_notifications(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Отправка напоминаний о поездках"""
    try:
        # Отправляем напоминания в фоновом режиме
        background_tasks.add_task(
            notification_service.send_reminder_notifications,
            db=db
        )
        
        return {
            "success": True,
            "message": "Напоминания поставлены в очередь"
        }
        
    except Exception as e:
        logger.error(f"Ошибка отправки напоминаний: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка отправки напоминаний"
        )

@router.get("/test/{user_id}")
async def test_notification(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Тестовое уведомление"""
    try:
        # Получаем пользователя
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Отправляем тестовое уведомление
        background_tasks.add_task(
            notification_service.send_system_notification,
            user=user,
            title="Тестовое уведомление",
            message="Это тестовое уведомление для проверки работы системы.",
            notification_type="info",
            db=db
        )
        
        return {
            "success": True,
            "message": "Тестовое уведомление отправлено"
        }
        
    except Exception as e:
        logger.error(f"Ошибка отправки тестового уведомления: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка отправки тестового уведомления"
        )

@router.get("/status")
async def get_notification_status():
    """Статус сервиса уведомлений"""
    try:
        # Проверяем доступность Telegram Bot API
        session = await notification_service.get_session()
        
        async with session.get(f"{notification_service.base_url}/getMe") as response:
            if response.status == 200:
                result = await response.json()
                if result.get("ok"):
                    bot_info = result.get("result", {})
                    return {
                        "status": "active",
                        "bot_name": bot_info.get("first_name", ""),
                        "bot_username": bot_info.get("username", ""),
                        "message": "Сервис уведомлений работает"
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Ошибка Telegram Bot API"
                    }
            else:
                return {
                    "status": "error",
                    "message": f"HTTP ошибка {response.status}"
                }
                
    except Exception as e:
        logger.error(f"Ошибка проверки статуса уведомлений: {str(e)}")
        return {
            "status": "error",
            "message": f"Ошибка подключения: {str(e)}"
        }

@router.get("/settings/{user_id}")
async def get_notification_settings(user_id: int, db: Session = Depends(get_db)):
    """Получение настроек уведомлений пользователя"""
    try:
        from ..models.notification import NotificationSettings
        
        settings = db.query(NotificationSettings).filter(
            NotificationSettings.user_id == user_id
        ).first()
        
        if not settings:
            # Создаем настройки по умолчанию
            settings = NotificationSettings(user_id=user_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return {
            "user_id": settings.user_id,
            "ride_notifications": settings.ride_notifications,
            "system_notifications": settings.system_notifications,
            "reminder_notifications": settings.reminder_notifications,
            "marketing_notifications": settings.marketing_notifications,
            "quiet_hours_start": settings.quiet_hours_start,
            "quiet_hours_end": settings.quiet_hours_end
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения настроек уведомлений: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения настроек"
        )

@router.put("/settings/{user_id}")
async def update_notification_settings(
    user_id: int, 
    settings_data: NotificationSettings,
    db: Session = Depends(get_db)
):
    """Обновление настроек уведомлений пользователя"""
    try:
        from ..models.notification import NotificationSettings
        
        settings = db.query(NotificationSettings).filter(
            NotificationSettings.user_id == user_id
        ).first()
        
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            db.add(settings)
        
        # Обновляем настройки
        settings.ride_notifications = settings_data.ride_notifications
        settings.system_notifications = settings_data.system_notifications
        settings.reminder_notifications = settings_data.reminder_notifications
        settings.marketing_notifications = settings_data.marketing_notifications
        settings.quiet_hours_start = settings_data.quiet_hours_start
        settings.quiet_hours_end = settings_data.quiet_hours_end
        
        db.commit()
        db.refresh(settings)
        
        return {
            "success": True,
            "message": "Настройки уведомлений обновлены"
        }
        
    except Exception as e:
        logger.error(f"Ошибка обновления настроек уведомлений: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обновления настроек"
        ) 