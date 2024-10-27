from typing import Optional

from pydantic import BaseModel

# Define Pydantic models for request and response data
class MessageSchema(BaseModel):
    content: str


class MessageRequestSchema(MessageSchema):
    role: str = "user"
    session_id: Optional[int] = None

class RawAIMessageResponseSchema(MessageSchema):
    # only used by the module `backend.utils.chat_completions_handler.get_openai_response`
    role: str = "assistant"

class AIMessageResponseSchema(MessageSchema):
    role: str = "assistant"
    session_id: Optional[int] = None
