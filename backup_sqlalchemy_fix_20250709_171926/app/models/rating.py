from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 звезд
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="ratings_given")
    target_user = relationship("User", foreign_keys=[target_user_id], back_populates="ratings_received")
    ride = relationship("Ride", back_populates="ratings")

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_rating_from_user', 'from_user_id'),
        Index('idx_rating_target_user', 'target_user_id'),
        Index('idx_rating_ride', 'ride_id'),
        Index('idx_rating_created', 'created_at'),
    )

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False)
    text = Column(Text, nullable=False)
    is_positive = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="reviews_given")
    target_user = relationship("User", foreign_keys=[target_user_id], back_populates="reviews_received")
    ride = relationship("Ride", back_populates="reviews")

    # Индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_review_from_user', 'from_user_id'),
        Index('idx_review_target_user', 'target_user_id'),
        Index('idx_review_ride', 'ride_id'),
        Index('idx_review_positive', 'is_positive'),
        Index('idx_review_created', 'created_at'),
    ) 