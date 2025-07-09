from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChatMessageBase(BaseModel):
    message: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageUpdate(ChatMessageBase):
    pass

class ChatMessageRead(ChatMessageBase):
    id: int
    chat_id: int
    user_from_id: int
    user_to_id: int
    is_read: bool
    read_at: Optional[datetime]
    timestamp: datetime

    class Config:
        from_attributes = True

# Alias for backward compatibility
MessageCreate = ChatMessageCreate
MessageUpdate = ChatMessageUpdate
MessageRead = ChatMessageRead

class ChatBase(BaseModel):
    ride_id: int
    user1_id: int
    user2_id: int

class ChatCreate(ChatBase):
    pass

class ChatUpdate(ChatBase):
    pass

class ChatRead(ChatBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChatWithDetails(ChatRead):
    last_message: Optional[ChatMessageRead]
    unread_count: int
    other_user: Optional[dict]
    ride: Optional[dict]

class ChatListResponse(BaseModel):
    chats: List[ChatWithDetails]
    total: int
    unread_total: int 