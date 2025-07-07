from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Upload(Base):
    __tablename__ = 'uploads'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow) 