from pydantic import BaseModel

from datetime import datetime
from typing import Optional

class ChatSessionSchema(BaseModel):
    user_id: int
    start_timestamp: datetime

class ChatSessionRequestSchema(ChatSessionSchema):
    session_id: Optional[int] = None

class ChatSessionResponseSchema(ChatSessionSchema):
    session_id: int