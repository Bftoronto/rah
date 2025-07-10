"""
WebSocket менеджер для уведомлений в реальном времени
"""

import asyncio
import json
import uuid
from typing import Dict, Set, List, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from .logger import get_logger

logger = get_logger("websocket_manager")

class NotificationMessage(BaseModel):
    """Схема сообщения уведомления"""
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()
    user_id: Optional[int] = None

class WebSocketConnection:
    """Класс для управления WebSocket соединением"""
    
    def __init__(self, websocket: WebSocket, user_id: Optional[int] = None):
        self.websocket = websocket
        self.user_id = user_id
        self.connection_id = str(uuid.uuid4())
        self.connected_at = datetime.now()
        self.last_activity = datetime.now()
        self.subscriptions: Set[str] = set()
    
    async def send_message(self, message: NotificationMessage):
        """Отправляет сообщение через WebSocket"""
        try:
            await self.websocket.send_text(message.json())
            self.last_activity = datetime.now()
            logger.debug(f"Сообщение отправлено пользователю {self.user_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            raise
    
    async def send_json(self, data: Dict[str, Any]):
        """Отправляет JSON данные через WebSocket"""
        try:
            await self.websocket.send_text(json.dumps(data))
            self.last_activity = datetime.now()
        except Exception as e:
            logger.error(f"Ошибка отправки JSON: {e}")
            raise
    
    def add_subscription(self, subscription: str):
        """Добавляет подписку"""
        self.subscriptions.add(subscription)
        logger.debug(f"Добавлена подписка {subscription} для пользователя {self.user_id}")
    
    def remove_subscription(self, subscription: str):
        """Удаляет подписку"""
        self.subscriptions.discard(subscription)
        logger.debug(f"Удалена подписка {subscription} для пользователя {self.user_id}")
    
    def is_subscribed_to(self, subscription: str) -> bool:
        """Проверяет, подписан ли пользователь на уведомления"""
        return subscription in self.subscriptions

class WebSocketManager:
    """Менеджер WebSocket соединений"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[int, Set[str]] = {}  # user_id -> connection_ids
        self.subscription_connections: Dict[str, Set[str]] = {}  # subscription -> connection_ids
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_failed': 0
        }
    
    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None) -> str:
        """Подключает нового пользователя"""
        await websocket.accept()
        
        connection = WebSocketConnection(websocket, user_id)
        self.active_connections[connection.connection_id] = connection
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection.connection_id)
        
        self.stats['total_connections'] += 1
        self.stats['active_connections'] += 1
        
        logger.info(f"WebSocket подключен: {connection.connection_id} для пользователя {user_id}")
        return connection.connection_id
    
    def disconnect(self, connection_id: str):
        """Отключает пользователя"""
        if connection_id in self.active_connections:
            connection = self.active_connections[connection_id]
            
            # Удаляем из подписок
            for subscription in connection.subscriptions:
                if subscription in self.subscription_connections:
                    self.subscription_connections[subscription].discard(connection_id)
                    if not self.subscription_connections[subscription]:
                        del self.subscription_connections[subscription]
            
            # Удаляем из пользовательских соединений
            if connection.user_id and connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]
            
            del self.active_connections[connection_id]
            self.stats['active_connections'] -= 1
            
            logger.info(f"WebSocket отключен: {connection_id}")
    
    async def subscribe(self, connection_id: str, subscription: str):
        """Подписывает соединение на уведомления"""
        if connection_id in self.active_connections:
            connection = self.active_connections[connection_id]
            connection.add_subscription(subscription)
            
            if subscription not in self.subscription_connections:
                self.subscription_connections[subscription] = set()
            self.subscription_connections[subscription].add(connection_id)
            
            # Отправляем подтверждение подписки
            await connection.send_json({
                "type": "subscription_confirmed",
                "subscription": subscription,
                "timestamp": datetime.now().isoformat()
            })
    
    async def unsubscribe(self, connection_id: str, subscription: str):
        """Отписывает соединение от уведомлений"""
        if connection_id in self.active_connections:
            connection = self.active_connections[connection_id]
            connection.remove_subscription(subscription)
            
            if subscription in self.subscription_connections:
                self.subscription_connections[subscription].discard(connection_id)
                if not self.subscription_connections[subscription]:
                    del self.subscription_connections[subscription]
            
            # Отправляем подтверждение отписки
            await connection.send_json({
                "type": "unsubscription_confirmed",
                "subscription": subscription,
                "timestamp": datetime.now().isoformat()
            })
    
    async def send_to_user(self, user_id: int, message: NotificationMessage):
        """Отправляет уведомление конкретному пользователю"""
        if user_id in self.user_connections:
            failed_sends = 0
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_message(message)
                        self.stats['messages_sent'] += 1
                    except Exception as e:
                        logger.error(f"Ошибка отправки пользователю {user_id}: {e}")
                        failed_sends += 1
                        self.stats['messages_failed'] += 1
            
            if failed_sends > 0:
                logger.warning(f"Не удалось отправить {failed_sends} сообщений пользователю {user_id}")
    
    async def send_to_subscription(self, subscription: str, message: NotificationMessage):
        """Отправляет уведомление всем подписчикам"""
        if subscription in self.subscription_connections:
            failed_sends = 0
            for connection_id in self.subscription_connections[subscription]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_message(message)
                        self.stats['messages_sent'] += 1
                    except Exception as e:
                        logger.error(f"Ошибка отправки подписчику {connection_id}: {e}")
                        failed_sends += 1
                        self.stats['messages_failed'] += 1
            
            if failed_sends > 0:
                logger.warning(f"Не удалось отправить {failed_sends} сообщений подписчикам {subscription}")
    
    async def broadcast(self, message: NotificationMessage):
        """Отправляет уведомление всем подключенным пользователям"""
        failed_sends = 0
        for connection in self.active_connections.values():
            try:
                await connection.send_message(message)
                self.stats['messages_sent'] += 1
            except Exception as e:
                logger.error(f"Ошибка broadcast: {e}")
                failed_sends += 1
                self.stats['messages_failed'] += 1
        
        if failed_sends > 0:
            logger.warning(f"Не удалось отправить {failed_sends} broadcast сообщений")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получает статистику WebSocket менеджера"""
        return {
            **self.stats,
            'subscriptions_count': len(self.subscription_connections),
            'users_connected': len(self.user_connections),
            'subscription_types': list(self.subscription_connections.keys())
        }
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Получает информацию о соединении"""
        if connection_id in self.active_connections:
            connection = self.active_connections[connection_id]
            return {
                'connection_id': connection.connection_id,
                'user_id': connection.user_id,
                'connected_at': connection.connected_at.isoformat(),
                'last_activity': connection.last_activity.isoformat(),
                'subscriptions': list(connection.subscriptions)
            }
        return None

# Глобальный экземпляр WebSocket менеджера
websocket_manager = WebSocketManager()

async def handle_websocket_connection(websocket: WebSocket, user_id: Optional[int] = None):
    """Обработчик WebSocket соединения"""
    connection_id = await websocket_manager.connect(websocket, user_id)
    
    try:
        while True:
            # Получаем сообщение от клиента
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Обрабатываем команды
            if message.get('type') == 'subscribe':
                subscription = message.get('subscription')
                if subscription:
                    await websocket_manager.subscribe(connection_id, subscription)
            
            elif message.get('type') == 'unsubscribe':
                subscription = message.get('subscription')
                if subscription:
                    await websocket_manager.unsubscribe(connection_id, subscription)
            
            elif message.get('type') == 'ping':
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket отключен: {connection_id}")
    except Exception as e:
        logger.error(f"Ошибка WebSocket соединения: {e}")
    finally:
        websocket_manager.disconnect(connection_id)

async def send_notification_to_user(user_id: int, notification_type: str, title: str, message: str, data: Optional[Dict[str, Any]] = None):
    """Отправляет уведомление пользователю через WebSocket"""
    notification = NotificationMessage(
        type=notification_type,
        title=title,
        message=message,
        data=data,
        user_id=user_id
    )
    
    await websocket_manager.send_to_user(user_id, notification)
    logger.info(f"Уведомление отправлено пользователю {user_id}: {title}")

async def send_notification_to_subscription(subscription: str, notification_type: str, title: str, message: str, data: Optional[Dict[str, Any]] = None):
    """Отправляет уведомление подписчикам через WebSocket"""
    notification = NotificationMessage(
        type=notification_type,
        title=title,
        message=message,
        data=data
    )
    
    await websocket_manager.send_to_subscription(subscription, notification)
    logger.info(f"Уведомление отправлено подписчикам {subscription}: {title}")

async def broadcast_notification(notification_type: str, title: str, message: str, data: Optional[Dict[str, Any]] = None):
    """Отправляет уведомление всем подключенным пользователям"""
    notification = NotificationMessage(
        type=notification_type,
        title=title,
        message=message,
        data=data
    )
    
    await websocket_manager.broadcast(notification)
    logger.info(f"Broadcast уведомление: {title}") 