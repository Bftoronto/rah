from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import uuid

class ModerationReport(Base):
    __tablename__ = 'moderation_reports'
    
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    target_type = Column(String, nullable=False)  # 'user', 'ride', 'message'
    target_id = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)  # 'spam', 'inappropriate', 'fraud', 'other'
    description = Column(Text)
    status = Column(String, default='pending')  # 'pending', 'resolved', 'dismissed'
    created_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)
    
    # Связи
    reporter = relationship("User", foreign_keys=[reporter_id])
    actions = relationship("ModerationAction", back_populates="report")
    
    def to_dict(self):
        return {
            "id": self.id,
            "reporter_id": self.reporter_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "reason": self.reason,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }

class ModerationAction(Base):
    __tablename__ = 'moderation_actions'
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey('moderation_reports.id'), nullable=False)
    moderator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String, nullable=False)  # 'warn', 'suspend', 'ban', 'hide', 'delete'
    reason = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Связи
    report = relationship("ModerationReport", back_populates="actions")
    moderator = relationship("User", foreign_keys=[moderator_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "report_id": self.report_id,
            "moderator_id": self.moderator_id,
            "action": self.action,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ModerationRule(Base):
    __tablename__ = 'moderation_rules'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    pattern = Column(String, nullable=False)  # Регулярное выражение
    action = Column(String, nullable=False)  # 'block', 'flag', 'warn'
    severity = Column(String, default='medium')  # 'low', 'medium', 'high'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "pattern": self.pattern,
            "action": self.action,
            "severity": self.severity,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ContentFilter(Base):
    __tablename__ = 'content_filters'
    
    id = Column(Integer, primary_key=True, index=True)
    filter_type = Column(String, nullable=False)  # 'word', 'phrase', 'regex'
    content = Column(String, nullable=False)
    replacement = Column(String, default='***')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "filter_type": self.filter_type,
            "content": self.content,
            "replacement": self.replacement,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class TrustScore(Base):
    __tablename__ = 'trust_scores'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    score = Column(Integer, default=100)
    level = Column(String, default='medium')  # 'low', 'medium', 'high', 'suspicious'
    warnings_count = Column(Integer, default=0)
    reports_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Связи
    user = relationship("User", foreign_keys=[user_id])
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "score": self.score,
            "level": self.level,
            "warnings_count": self.warnings_count,
            "reports_count": self.reports_count,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        } 