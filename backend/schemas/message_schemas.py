from typing import Optional

from pydantic import BaseModel


# Define Pydantic models for request and response data
class MessageSchema(BaseModel):
    role: str
    message: str


class MessageRequestSchema(MessageSchema):
    pass


class MessageHistorySchema(MessageSchema):
    pass


class AIResponseSchema(BaseModel):
    ai_response: str
    session_id: Optional[int]
