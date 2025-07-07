from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import json

from ..models.chat import ChatMessage, Chat
from ..models.user import User
from ..models.ride import Ride
from ..schemas.chat import ChatMessageCreate, ChatMessageRead, ChatCreate, ChatRead
from ..database import get_db

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.db: Session = next(get_db())
    
    def create_chat(self, ride_id: int, user1_id: int, user2_id: int) -> Chat:
        """Создание нового чата между пользователями"""
        try:
            # Проверка существования поездки
            ride = self.db.query(Ride).filter(Ride.id == ride_id).first()
            if not ride:
                raise ValueError("Поездка не найдена")
            
            # Проверка, что пользователи связаны с поездкой
            if not (ride.driver_id in [user1_id, user2_id] and 
                   ride.passenger_id in [user1_id, user2_id]):
                raise ValueError("Пользователи должны быть связаны с поездкой")
            
            # Проверка существования чата
            existing_chat = self.db.query(Chat).filter(
                and_(
                    Chat.ride_id == ride_id,
                    or_(
                        and_(Chat.user1_id == user1_id, Chat.user2_id == user2_id),
                        and_(Chat.user1_id == user2_id, Chat.user2_id == user1_id)
                    )
                )
            ).first()
            
            if existing_chat:
                return existing_chat
            
            # Создание нового чата
            chat = Chat(
                ride_id=ride_id,
                user1_id=min(user1_id, user2_id),
                user2_id=max(user1_id, user2_id),
                created_at=datetime.utcnow()
            )
            
            self.db.add(chat)
            self.db.commit()
            self.db.refresh(chat)
            
            logger.info(f"Создан чат {chat.id} для поездки {ride_id}")
            return chat
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка создания чата: {e}")
            raise
    
    def get_chat(self, chat_id: int, user_id: int) -> Optional[Chat]:
        """Получение чата с проверкой прав доступа"""
        try:
            chat = self.db.query(Chat).filter(
                and_(
                    Chat.id == chat_id,
                    or_(Chat.user1_id == user_id, Chat.user2_id == user_id)
                )
            ).first()
            
            return chat
        except Exception as e:
            logger.error(f"Ошибка получения чата {chat_id}: {e}")
            raise
    
    def get_user_chats(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение всех чатов пользователя"""
        try:
            chats = self.db.query(Chat).filter(
                or_(Chat.user1_id == user_id, Chat.user2_id == user_id)
            ).order_by(desc(Chat.updated_at)).limit(limit).offset(offset).all()
            
            chats_with_details = []
            for chat in chats:
                # Получение последнего сообщения
                last_message = self.db.query(ChatMessage).filter(
                    ChatMessage.chat_id == chat.id
                ).order_by(desc(ChatMessage.timestamp)).first()
                
                # Получение информации о собеседнике
                other_user_id = chat.user2_id if chat.user1_id == user_id else chat.user1_id
                other_user = self.db.query(User).filter(User.id == other_user_id).first()
                
                # Получение информации о поездке
                ride = self.db.query(Ride).filter(Ride.id == chat.ride_id).first()
                
                chat_info = {
                    "id": chat.id,
                    "ride_id": chat.ride_id,
                    "other_user": {
                        "id": other_user.id,
                        "full_name": other_user.full_name,
                        "avatar_url": other_user.avatar_url
                    } if other_user else None,
                    "ride": {
                        "id": ride.id,
                        "from_location": ride.from_location,
                        "to_location": ride.to_location,
                        "date": ride.date,
                        "status": ride.status
                    } if ride else None,
                    "last_message": {
                        "id": last_message.id,
                        "message": last_message.message,
                        "timestamp": last_message.timestamp,
                        "user_from_id": last_message.user_from_id
                    } if last_message else None,
                    "unread_count": self.get_unread_count(chat.id, user_id),
                    "created_at": chat.created_at,
                    "updated_at": chat.updated_at
                }
                
                chats_with_details.append(chat_info)
            
            return chats_with_details
            
        except Exception as e:
            logger.error(f"Ошибка получения чатов пользователя {user_id}: {e}")
            raise
    
    def send_message(self, chat_id: int, user_id: int, message_data: ChatMessageCreate) -> ChatMessage:
        """Отправка сообщения в чат"""
        try:
            # Проверка доступа к чату
            chat = self.get_chat(chat_id, user_id)
            if not chat:
                raise ValueError("Чат не найден или нет доступа")
            
            # Валидация сообщения
            if not message_data.message or len(message_data.message.strip()) == 0:
                raise ValueError("Сообщение не может быть пустым")
            
            if len(message_data.message) > 1000:
                raise ValueError("Сообщение слишком длинное (максимум 1000 символов)")
            
            # Создание сообщения
            message = ChatMessage(
                chat_id=chat_id,
                user_from_id=user_id,
                user_to_id=chat.user2_id if chat.user1_id == user_id else chat.user1_id,
                message=message_data.message.strip(),
                timestamp=datetime.utcnow()
            )
            
            self.db.add(message)
            
            # Обновление времени последнего сообщения в чате
            chat.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Отправлено сообщение {message.id} в чат {chat_id}")
            return message
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
            raise
    
    def get_messages(self, chat_id: int, user_id: int, limit: int = 50, offset: int = 0) -> List[ChatMessage]:
        """Получение сообщений чата"""
        try:
            # Проверка доступа к чату
            chat = self.get_chat(chat_id, user_id)
            if not chat:
                raise ValueError("Чат не найден или нет доступа")
            
            messages = self.db.query(ChatMessage).filter(
                ChatMessage.chat_id == chat_id
            ).order_by(desc(ChatMessage.timestamp)).limit(limit).offset(offset).all()
            
            # Отметка сообщений как прочитанные
            self.mark_messages_as_read(chat_id, user_id)
            
            return messages
            
        except Exception as e:
            logger.error(f"Ошибка получения сообщений чата {chat_id}: {e}")
            raise
    
    def mark_messages_as_read(self, chat_id: int, user_id: int) -> int:
        """Отметка сообщений как прочитанные"""
        try:
            # Получение непрочитанных сообщений
            unread_messages = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.chat_id == chat_id,
                    ChatMessage.user_to_id == user_id,
                    ChatMessage.is_read == False
                )
            ).all()
            
            count = 0
            for message in unread_messages:
                message.is_read = True
                message.read_at = datetime.utcnow()
                count += 1
            
            self.db.commit()
            
            if count > 0:
                logger.info(f"Отмечено {count} сообщений как прочитанные в чате {chat_id}")
            
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка отметки сообщений как прочитанные в чате {chat_id}: {e}")
            raise
    
    def get_unread_count(self, chat_id: int, user_id: int) -> int:
        """Получение количества непрочитанных сообщений"""
        try:
            count = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.chat_id == chat_id,
                    ChatMessage.user_to_id == user_id,
                    ChatMessage.is_read == False
                )
            ).count()
            
            return count
            
        except Exception as e:
            logger.error(f"Ошибка получения количества непрочитанных сообщений: {e}")
            return 0
    
    def get_total_unread_count(self, user_id: int) -> int:
        """Получение общего количества непрочитанных сообщений пользователя"""
        try:
            count = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.user_to_id == user_id,
                    ChatMessage.is_read == False
                )
            ).count()
            
            return count
            
        except Exception as e:
            logger.error(f"Ошибка получения общего количества непрочитанных сообщений: {e}")
            return 0
    
    def delete_message(self, message_id: int, user_id: int) -> bool:
        """Удаление сообщения (только своим)"""
        try:
            message = self.db.query(ChatMessage).filter(
                and_(
                    ChatMessage.id == message_id,
                    ChatMessage.user_from_id == user_id
                )
            ).first()
            
            if not message:
                raise ValueError("Сообщение не найдено или нет прав на удаление")
            
            # Проверка времени (можно удалить только в течение 1 часа)
            if datetime.utcnow() - message.timestamp > timedelta(hours=1):
                raise ValueError("Сообщение можно удалить только в течение часа после отправки")
            
            self.db.delete(message)
            self.db.commit()
            
            logger.info(f"Удалено сообщение {message_id} пользователем {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка удаления сообщения {message_id}: {e}")
            raise
    
    def get_chat_statistics(self, user_id: int) -> Dict[str, Any]:
        """Получение статистики чатов пользователя"""
        try:
            # Общее количество чатов
            total_chats = self.db.query(Chat).filter(
                or_(Chat.user1_id == user_id, Chat.user2_id == user_id)
            ).count()
            
            # Общее количество сообщений
            total_messages = self.db.query(ChatMessage).filter(
                ChatMessage.user_from_id == user_id
            ).count()
            
            # Непрочитанные сообщения
            unread_messages = self.get_total_unread_count(user_id)
            
            # Активные чаты (с сообщениями за последние 7 дней)
            week_ago = datetime.utcnow() - timedelta(days=7)
            active_chats = self.db.query(Chat).join(ChatMessage).filter(
                and_(
                    or_(Chat.user1_id == user_id, Chat.user2_id == user_id),
                    ChatMessage.timestamp >= week_ago
                )
            ).distinct().count()
            
            stats = {
                "total_chats": total_chats,
                "total_messages": total_messages,
                "unread_messages": unread_messages,
                "active_chats": active_chats
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики чатов пользователя {user_id}: {e}")
            raise
    
    def cleanup_old_messages(self, days: int = 30) -> int:
        """Очистка старых сообщений"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            old_messages = self.db.query(ChatMessage).filter(
                ChatMessage.timestamp < cutoff_date
            ).all()
            
            count = 0
            for message in old_messages:
                self.db.delete(message)
                count += 1
            
            self.db.commit()
            
            logger.info(f"Очищено {count} старых сообщений")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Ошибка очистки старых сообщений: {e}")
            raise

# Создание экземпляра сервиса
chat_service = ChatService() 