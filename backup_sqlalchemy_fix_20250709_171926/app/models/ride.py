from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Ride(Base):
    __tablename__ = 'rides'
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey('users.id'))
    passenger_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    from_location = Column(String, nullable=False)
    to_location = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    seats = Column(Integer, nullable=False)
    status = Column(String, default="active")  # active, completed, cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Отношения
    driver = relationship('User', foreign_keys=[driver_id])
    passenger = relationship('User', foreign_keys=[passenger_id])
    ratings = relationship("Rating", back_populates="ride")
    reviews = relationship("Review", back_populates="ride")
    chats = relationship("Chat", back_populates="ride")
 