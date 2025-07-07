from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Chat(Base):
    __tablename__ = 'chats'
    
    id = Column(Integer, primary_key=True, index=True)
    ride_id = Column(Integer, ForeignKey('rides.id'), nullable=False)
    user1_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Отношения
    ride = relationship("Ride", back_populates="chats")
    user1 = relationship("User", foreign_keys=[user1_id])
    user2 = relationship("User", foreign_keys=[user2_id])
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id'), nullable=False)
    user_from_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_to_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Отношения
    chat = relationship("Chat", back_populates="messages")
    user_from = relationship("User", foreign_keys=[user_from_id])
    user_to = relationship("User", foreign_keys=[user_to_id]) 