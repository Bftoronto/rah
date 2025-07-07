from fastapi import APIRouter, HTTPException, Depends, Query, Path, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging
import json

from ..schemas.chat import ChatMessageCreate, ChatMessageRead, ChatCreate, ChatRead, ChatListResponse
from ..services.chat_service import chat_service
from ..services.auth_service import get_current_user
from ..models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)

# Хранилище активных WebSocket соединений
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"Пользователь {user_id} подключился к WebSocket")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"Пользователь {user_id} отключился от WebSocket")

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
                self.disconnect(user_id)

    async def broadcast(self, message: str):
        disconnected_users = []
        for user_id, connection in self.active_connections.items():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Удаление отключенных соединений
        for user_id in disconnected_users:
            self.disconnect(user_id)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket эндпоинт для real-time чата"""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Получение сообщения от клиента
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Обработка сообщения
            if message_data.get("type") == "message":
                try:
                    # Создание сообщения в базе данных
                    chat_message = ChatMessageCreate(message=message_data.get("message", ""))
                    message = chat_service.send_message(
                        message_data.get("chat_id"), 
                        user_id, 
                        chat_message
                    )
                    
                    # Отправка сообщения получателю
                    chat = chat_service.get_chat(message_data.get("chat_id"), user_id)
                    if chat:
                        recipient_id = chat.user2_id if chat.user1_id == user_id else chat.user1_id
                        
                        # Подготовка сообщения для отправки
                        response_message = {
                            "type": "new_message",
                            "chat_id": message.chat_id,
                            "message": {
                                "id": message.id,
                                "message": message.message,
                                "timestamp": message.timestamp.isoformat(),
                                "user_from_id": message.user_from_id,
                                "user_to_id": message.user_to_id
                            }
                        }
                        
                        # Отправка получателю
                        await manager.send_personal_message(
                            json.dumps(response_message), 
                            recipient_id
                        )
                        
                        # Подтверждение отправителю
                        await manager.send_personal_message(
                            json.dumps({"type": "message_sent", "message_id": message.id}), 
                            user_id
                        )
                        
                except Exception as e:
                    logger.error(f"Ошибка обработки WebSocket сообщения: {e}")
                    await manager.send_personal_message(
                        json.dumps({"type": "error", "message": "Ошибка отправки сообщения"}), 
                        user_id
                    )
            
            elif message_data.get("type") == "typing":
                # Уведомление о наборе текста
                chat_id = message_data.get("chat_id")
                chat = chat_service.get_chat(chat_id, user_id)
                if chat:
                    recipient_id = chat.user2_id if chat.user1_id == user_id else chat.user1_id
                    typing_message = {
                        "type": "typing",
                        "chat_id": chat_id,
                        "user_id": user_id
                    }
                    await manager.send_personal_message(
                        json.dumps(typing_message), 
                        recipient_id
                    )
            
            elif message_data.get("type") == "read":
                # Отметка сообщений как прочитанные
                chat_id = message_data.get("chat_id")
                try:
                    count = chat_service.mark_messages_as_read(chat_id, user_id)
                    if count > 0:
                        # Уведомление отправителя о прочтении
                        chat = chat_service.get_chat(chat_id, user_id)
                        if chat:
                            sender_id = chat.user1_id if chat.user2_id == user_id else chat.user2_id
                            read_message = {
                                "type": "messages_read",
                                "chat_id": chat_id,
                                "user_id": user_id,
                                "count": count
                            }
                            await manager.send_personal_message(
                                json.dumps(read_message), 
                                sender_id
                            )
                except Exception as e:
                    logger.error(f"Ошибка отметки сообщений как прочитанные: {e}")
                    
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"Ошибка WebSocket соединения для пользователя {user_id}: {e}")
        manager.disconnect(user_id)

@router.post("/", response_model=ChatRead)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user)
):
    """Создание нового чата"""
    try:
        # Определяем второго пользователя
        if chat_data.user1_id == current_user.id:
            user2_id = chat_data.user2_id
        elif chat_data.user2_id == current_user.id:
            user2_id = chat_data.user1_id
        else:
            raise HTTPException(status_code=403, detail="Нет прав на создание чата")
        
        chat = chat_service.create_chat(chat_data.ride_id, current_user.id, user2_id)
        return chat
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка создания чата: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/", response_model=ChatListResponse)
async def get_my_chats(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Количество чатов"),
    offset: int = Query(0, ge=0, description="Смещение")
):
    """Получение всех чатов пользователя"""
    try:
        chats = chat_service.get_user_chats(current_user.id, limit, offset)
        unread_total = chat_service.get_total_unread_count(current_user.id)
        
        return {
            "chats": chats,
            "total": len(chats),
            "unread_total": unread_total
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения чатов пользователя {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/{chat_id}/messages", response_model=List[ChatMessageRead])
async def get_chat_messages(
    chat_id: int = Path(..., description="ID чата"),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Количество сообщений"),
    offset: int = Query(0, ge=0, description="Смещение")
):
    """Получение сообщений чата"""
    try:
        messages = chat_service.get_messages(chat_id, current_user.id, limit, offset)
        return messages
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка получения сообщений чата {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post("/{chat_id}/send", response_model=ChatMessageRead)
async def send_message(
    chat_id: int = Path(..., description="ID чата"),
    message_data: ChatMessageCreate = ...,
    current_user: User = Depends(get_current_user)
):
    """Отправка сообщения в чат"""
    try:
        message = chat_service.send_message(chat_id, current_user.id, message_data)
        return message
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.put("/{chat_id}/read", response_model=Dict[str, Any])
async def mark_chat_as_read(
    chat_id: int = Path(..., description="ID чата"),
    current_user: User = Depends(get_current_user)
):
    """Отметка сообщений чата как прочитанные"""
    try:
        count = chat_service.mark_messages_as_read(chat_id, current_user.id)
        
        return {
            "message": f"Отмечено {count} сообщений как прочитанные",
            "chat_id": chat_id,
            "marked_count": count
        }
        
    except Exception as e:
        logger.error(f"Ошибка отметки сообщений как прочитанные в чате {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.delete("/messages/{message_id}", response_model=Dict[str, Any])
async def delete_message(
    message_id: int = Path(..., description="ID сообщения"),
    current_user: User = Depends(get_current_user)
):
    """Удаление сообщения"""
    try:
        success = chat_service.delete_message(message_id, current_user.id)
        
        return {
            "message": "Сообщение успешно удалено",
            "message_id": message_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка удаления сообщения {message_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/statistics", response_model=Dict[str, Any])
async def get_chat_statistics(
    current_user: User = Depends(get_current_user)
):
    """Получение статистики чатов пользователя"""
    try:
        stats = chat_service.get_chat_statistics(current_user.id)
        return stats
        
    except Exception as e:
        logger.error(f"Ошибка получения статистики чатов пользователя {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/unread/count", response_model=Dict[str, Any])
async def get_unread_count(
    current_user: User = Depends(get_current_user)
):
    """Получение количества непрочитанных сообщений"""
    try:
        unread_total = chat_service.get_total_unread_count(current_user.id)
        
        return {
            "unread_count": unread_total,
            "user_id": current_user.id
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения количества непрочитанных сообщений: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/{chat_id}/info", response_model=Dict[str, Any])
async def get_chat_info(
    chat_id: int = Path(..., description="ID чата"),
    current_user: User = Depends(get_current_user)
):
    """Получение информации о чате"""
    try:
        chat = chat_service.get_chat(chat_id, current_user.id)
        if not chat:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        # Получение информации о собеседнике
        other_user_id = chat.user2_id if chat.user1_id == current_user.id else chat.user1_id
        other_user = chat.user2 if chat.user1_id == current_user.id else chat.user1
        
        # Получение количества непрочитанных сообщений
        unread_count = chat_service.get_unread_count(chat_id, current_user.id)
        
        # Получение последнего сообщения
        messages = chat_service.get_messages(chat_id, current_user.id, limit=1, offset=0)
        last_message = messages[0] if messages else None
        
        chat_info = {
            "id": chat.id,
            "ride_id": chat.ride_id,
            "other_user": {
                "id": other_user.id,
                "full_name": other_user.full_name,
                "avatar_url": other_user.avatar_url
            } if other_user else None,
            "unread_count": unread_count,
            "last_message": {
                "id": last_message.id,
                "message": last_message.message,
                "timestamp": last_message.timestamp,
                "user_from_id": last_message.user_from_id
            } if last_message else None,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at
        }
        
        return chat_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения информации о чате {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.post("/ride/{ride_id}/start", response_model=ChatRead)
async def start_chat_for_ride(
    ride_id: int = Path(..., description="ID поездки"),
    current_user: User = Depends(get_current_user)
):
    """Создание чата для поездки"""
    try:
        # Получение информации о поездке
        from ..services.ride_service import ride_service
        ride = ride_service.get_ride(ride_id)
        
        if not ride:
            raise HTTPException(status_code=404, detail="Поездка не найдена")
        
        # Определение второго пользователя
        if ride.driver_id == current_user.id:
            other_user_id = ride.passenger_id
        elif ride.passenger_id == current_user.id:
            other_user_id = ride.driver_id
        else:
            raise HTTPException(status_code=403, detail="Нет прав на создание чата для этой поездки")
        
        if not other_user_id:
            raise HTTPException(status_code=400, detail="Поездка должна быть забронирована")
        
        # Создание чата
        chat = chat_service.create_chat(ride_id, current_user.id, other_user_id)
        return chat
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ошибка создания чата для поездки {ride_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера") 