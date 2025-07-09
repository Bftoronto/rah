from pydantic import BaseModel
from datetime import datetime

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

# Alias for backward compatibility
UploadResponse = UploadRead 