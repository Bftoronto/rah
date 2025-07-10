from pydantic import BaseModel, validator, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class ReportCreate(BaseModel):
    target_type: str
    target_id: int
    reason: str
    description: Optional[str] = None
    
    @validator('target_type')
    def validate_target_type(cls, v):
        allowed_types = ['user', 'ride', 'message']
        if v not in allowed_types:
            raise ValueError(f"Неподдерживаемый тип цели: {v}")
        return v
    
    @validator('reason')
    def validate_reason(cls, v):
        allowed_reasons = ['spam', 'inappropriate', 'fraud', 'harassment', 'fake', 'other']
        if v not in allowed_reasons:
            raise ValueError(f"Неподдерживаемая причина: {v}")
        return v

class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    target_type: str
    target_id: int
    reason: str
    description: Optional[str]
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class ActionCreate(BaseModel):
    action: str
    reason: Optional[str] = None
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['warn', 'suspend', 'ban', 'hide', 'delete', 'dismiss']
        if v not in allowed_actions:
            raise ValueError(f"Неподдерживаемое действие: {v}")
        return v

class ActionResponse(BaseModel):
    id: int
    report_id: int
    moderator_id: int
    action: str
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class ContentCheckRequest(BaseModel):
    content: str
    content_type: str = "text"  # text, profile, ride
    
    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = ['text', 'profile', 'ride']
        if v not in allowed_types:
            raise ValueError(f"Неподдерживаемый тип контента: {v}")
        return v

class ContentCheckResponse(BaseModel):
    clean: bool
    score: int
    violations: List[Dict[str, Any]]
    requires_review: bool

    class Config:
        populate_by_name = True

class TrustScoreResponse(BaseModel):
    trust_score: int
    level: str
    warnings: int
    reports: int

    class Config:
        populate_by_name = True

class ModerationStatsResponse(BaseModel):
    period_days: int
    total_reports: int
    pending_reports: int
    resolved_reports: int
    action_stats: Dict[str, int]
    resolution_rate: float

    class Config:
        populate_by_name = True

class RuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    pattern: str
    action: str
    severity: str = "medium"
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['block', 'flag', 'warn']
        if v not in allowed_actions:
            raise ValueError(f"Неподдерживаемое действие: {v}")
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        allowed_severities = ['low', 'medium', 'high']
        if v not in allowed_severities:
            raise ValueError(f"Неподдерживаемая важность: {v}")
        return v

class RuleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    pattern: str
    action: str
    severity: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class FilterCreate(BaseModel):
    filter_type: str
    content: str
    replacement: str = "***"
    
    @validator('filter_type')
    def validate_filter_type(cls, v):
        allowed_types = ['word', 'phrase', 'regex']
        if v not in allowed_types:
            raise ValueError(f"Неподдерживаемый тип фильтра: {v}")
        return v

class FilterResponse(BaseModel):
    id: int
    filter_type: str
    content: str
    replacement: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
        populate_by_name = True

class UserViolationsResponse(BaseModel):
    reports: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]

    class Config:
        populate_by_name = True

class BulkActionRequest(BaseModel):
    report_ids: List[int]
    action: str
    reason: Optional[str] = None
    
    @validator('report_ids')
    def validate_report_ids(cls, v):
        if not v:
            raise ValueError("Список жалоб не может быть пустым")
        if len(v) > 100:
            raise ValueError("Максимум 100 жалоб за раз")
        return v
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['warn', 'suspend', 'ban', 'hide', 'delete', 'dismiss']
        if v not in allowed_actions:
            raise ValueError(f"Неподдерживаемое действие: {v}")
        return v

    class Config:
        populate_by_name = True

# Aliases for backward compatibility
ReportRead = ReportResponse
ReportUpdate = ReportCreate 