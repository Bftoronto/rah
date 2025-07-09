from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UploadBase(BaseModel):
    user_id: int
    file_url: str
    file_type: str

class UploadCreate(UploadBase):
    pass

class UploadRead(UploadBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    """Схема ответа для загрузки файлов"""
    success: bool
    file_url: str
    file_type: str
    original_filename: Optional[str] = None
    file_size: Optional[int] = None
    message: str
    
    class Config:
        from_attributes = True

# Alias for backward compatibility
UploadResponseLegacy = UploadRead 