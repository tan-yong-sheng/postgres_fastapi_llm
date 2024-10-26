from typing import Optional

from pydantic import BaseModel


# Define Pydantic models for request and response data
class MessageSchema(BaseModel):
    message: str


class MessageRequestSchema(MessageSchema):
    session_id: Optional[int] = None


class MessageHistorySchema(MessageSchema):
    pass


class AIResponseSchema(BaseModel):
    ai_response: str
    session_id: Optional[int] = None
