#!/bin/bash

# Fix Chat Schema Import Issues
# This script fixes missing schema classes that are causing import errors

set -e

echo "🔧 Fixing Chat Schema Import Issues..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "backend/app/schemas/chat.py" ]; then
    error "Chat schema file not found. Please run this script from the project root."
    exit 1
fi

log "Backing up current chat schema..."
cp backend/app/schemas/chat.py backend/app/schemas/chat.py.backup

log "Fixing chat schema imports..."

# Create the fixed chat schema content
cat > backend/app/schemas/chat.py << 'EOF'
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
        orm_mode = True

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
        orm_mode = True

class ChatWithDetails(ChatRead):
    last_message: Optional[ChatMessageRead]
    unread_count: int
    other_user: Optional[dict]
    ride: Optional[dict]

class ChatListResponse(BaseModel):
    chats: List[ChatWithDetails]
    total: int
    unread_total: int
EOF

log "Verifying the fix..."

# Test the import
cd backend
python3 -c "
try:
    from app.schemas.chat import ChatCreate, ChatUpdate, ChatRead, MessageCreate, MessageUpdate, MessageRead
    print('✅ All chat schema imports working correctly')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    log "✅ Chat schema imports fixed successfully!"
    log "Backup saved as: backend/app/schemas/chat.py.backup"
else
    error "Failed to fix chat schema imports"
    log "Restoring backup..."
    cp backend/app/schemas/chat.py.backup backend/app/schemas/chat.py
    exit 1
fi

log "🎉 Chat schema import fix completed successfully!" 