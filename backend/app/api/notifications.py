from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from ..database import get_db
from ..services.notification_service import NotificationService
from ..schemas.notification import (
    NotificationCreate, BulkNotificationCreate, NotificationResponse,
    NotificationSettings, NotificationStats
)
from ..utils.jwt_auth import get_current_user_id
from ..utils.websocket_manager import handle_websocket_connection, send_notification_to_user, send_notification_to_subscription, broadcast_notification
from ..schemas.responses import create_success_response, create_error_response, create_paginated_response
from ..utils.logger import get_logger

logger = get_logger("notification_api")
router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint для уведомлений в реальном времени
    
    Args:
        websocket: WebSocket соединение
        user_id: ID пользователя
    """
    await handle_websocket_connection(websocket, user_id)

@router.post("/send", response_model=dict)
async def send_notification(
    notification_data: NotificationCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Отправка уведомления пользователю
    
    Args:
        notification_data: Данные уведомления
        current_user_id: ID текущего пользователя
        db: Сессия базы данных
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        notification_service = NotificationService(db)
        
        # Отправляем уведомление через WebSocket
        await send_notification_to_user(
            user_id=notification_data.user_id,
            notification_type=notification_data.notification_type,
            title=notification_data.title or "Уведомление",
            message=notification_data.message or "",
            data=notification_data.ride_data
        )
        
        # Сохраняем в базе данных
        notification = notification_service.create_notification(notification_data, current_user_id)
        
        logger.info(f"Уведомление отправлено пользователю {notification_data.user_id}")
        
        return create_success_response(
            data={
                'notification_id': str(notification.id) if hasattr(notification, 'id') else None,
                'user_id': notification_data.user_id,
                'type': notification_data.notification_type,
                'sent_at': datetime.now().isoformat()
            },
            message="Уведомление успешно отправлено"
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {str(e)}")
        return create_error_response(
            message="Ошибка отправки уведомления",
            error_code="SEND_ERROR",
            user_id=current_user_id,
            request_id=str(uuid.uuid4())
        )

@router.post("/send/bulk", response_model=dict)
async def send_bulk_notification(
    notification_data: BulkNotificationCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Массовая отправка уведомлений
    
    Args:
        notification_data: Данные уведомления
        current_user_id: ID текущего пользователя
        db: Сессия базы данных
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        notification_service = NotificationService(db)
        
        # Отправляем уведомления через WebSocket
        for user_id in notification_data.user_ids:
            await send_notification_to_user(
                user_id=user_id,
                notification_type=notification_data.notification_type,
                title=notification_data.title,
                message=notification_data.message
            )
        
        # Сохраняем в базе данных
        notifications = notification_service.create_bulk_notifications(notification_data, current_user_id)
        
        logger.info(f"Массовое уведомление отправлено {len(notification_data.user_ids)} пользователям")
        
        return create_success_response(
            data={
                'sent_count': len(notification_data.user_ids),
                'notification_type': notification_data.notification_type,
                'sent_at': datetime.now().isoformat()
            },
            message=f"Уведомления отправлены {len(notification_data.user_ids)} пользователям"
        )
        
    except Exception as e:
        logger.error(f"Ошибка массовой отправки уведомлений: {str(e)}")
        return create_error_response(
            message="Ошибка массовой отправки уведомлений",
            error_code="BULK_SEND_ERROR",
            user_id=current_user_id,
            request_id=str(uuid.uuid4())
        )

@router.post("/send/ride", response_model=dict)
async def send_ride_notification(
    ride_id: int,
    notification_type: str,
    title: str,
    message: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Отправка уведомления о поездке
    
    Args:
        ride_id: ID поездки
        notification_type: Тип уведомления
        title: Заголовок
        message: Сообщение
        current_user_id: ID текущего пользователя
        db: Сессия базы данных
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        # Отправляем уведомление подписчикам поездки
        await send_notification_to_subscription(
            subscription=f"ride_{ride_id}",
            notification_type=notification_type,
            title=title,
            message=message,
            data={'ride_id': ride_id}
        )
        
        logger.info(f"Уведомление о поездке {ride_id} отправлено")
        
        return create_success_response(
            data={
                'ride_id': ride_id,
                'notification_type': notification_type,
                'sent_at': datetime.now().isoformat()
            },
            message="Уведомление о поездке отправлено"
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о поездке: {str(e)}")
        return create_error_response(
            message="Ошибка отправки уведомления о поездке",
            error_code="RIDE_NOTIFICATION_ERROR",
            user_id=current_user_id,
            request_id=str(uuid.uuid4())
        )

@router.post("/send/system", response_model=dict)
async def send_system_notification(
    title: str,
    message: str,
    notification_type: str = "system",
    current_user_id: int = Depends(get_current_user_id)
):
    """
    Отправка системного уведомления всем пользователям
    
    Args:
        title: Заголовок
        message: Сообщение
        notification_type: Тип уведомления
        current_user_id: ID текущего пользователя
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        # Отправляем broadcast уведомление
        await broadcast_notification(
            notification_type=notification_type,
            title=title,
            message=message
        )
        
        logger.info(f"Системное уведомление отправлено: {title}")
        
        return create_success_response(
            data={
                'notification_type': notification_type,
                'sent_at': datetime.now().isoformat()
            },
            message="Системное уведомление отправлено"
        )
        
    except Exception as e:
        logger.error(f"Ошибка отправки системного уведомления: {str(e)}")
        return create_error_response(
            message="Ошибка отправки системного уведомления",
            error_code="SYSTEM_NOTIFICATION_ERROR",
            user_id=current_user_id,
            request_id=str(uuid.uuid4())
        )

@router.get("/settings/{user_id}", response_model=dict)
def get_notification_settings(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение настроек уведомлений пользователя
    
    Args:
        user_id: ID пользователя
        db: Сессия базы данных
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        notification_service = NotificationService(db)
        settings = notification_service.get_notification_settings(user_id)
        
        return create_success_response(
            data=settings,
            message="Настройки уведомлений получены"
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения настроек уведомлений: {str(e)}")
        return create_error_response(
            message="Ошибка получения настроек уведомлений",
            error_code="SETTINGS_ERROR",
            user_id=user_id,
            request_id=str(uuid.uuid4())
        )

@router.put("/settings/{user_id}", response_model=dict)
def update_notification_settings(
    user_id: int,
    settings: NotificationSettings,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Обновление настроек уведомлений пользователя
    
    Args:
        user_id: ID пользователя
        settings: Новые настройки
        current_user_id: ID текущего пользователя
        db: Сессия базы данных
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        notification_service = NotificationService(db)
        updated_settings = notification_service.update_notification_settings(user_id, settings)
        
        logger.info(f"Настройки уведомлений обновлены для пользователя {user_id}")
        
        return create_success_response(
            data=updated_settings,
            message="Настройки уведомлений обновлены"
        )
        
    except Exception as e:
        logger.error(f"Ошибка обновления настроек уведомлений: {str(e)}")
        return create_error_response(
            message="Ошибка обновления настроек уведомлений",
            error_code="UPDATE_SETTINGS_ERROR",
            user_id=current_user_id,
            request_id=str(uuid.uuid4())
        )

@router.get("/stats", response_model=dict)
def get_notification_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Получение статистики уведомлений
    
    Args:
        current_user_id: ID текущего пользователя
        db: Сессия базы данных
    
    Returns:
        dict: Стандартизированный ответ
    """
    try:
        notification_service = NotificationService(db)
        stats = notification_service.get_notification_stats()
        
        return create_success_response(
            data=stats,
            message="Статистика уведомлений получена"
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики уведомлений: {str(e)}")
        return create_error_response(
            message="Ошибка получения статистики уведомлений",
            error_code="STATS_ERROR",
            user_id=current_user_id,
            request_id=str(uuid.uuid4())
        ) 