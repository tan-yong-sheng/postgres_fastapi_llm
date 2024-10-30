from pydantic import BaseModel, UUID4

from datetime import datetime
from typing import Optional, Annotated

class ChatSessionSchema(BaseModel):
    user_id: str 
    created_at: datetime

class ChatSessionRequestSchema(ChatSessionSchema):
    session_id: Optional[str] = None

class ChatSessionResponseSchema(ChatSessionSchema):
    session_id: str