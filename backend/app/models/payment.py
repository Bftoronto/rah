from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ride_id = Column(Integer, ForeignKey('rides.id'), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default='pending')  # pending, completed, failed, refunded
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Отношения
    user = relationship("User", back_populates="payments")
    ride = relationship("Ride", back_populates="payments") 