from typing import Optional

from pydantic import BaseModel

# suggestion: enum for role: "user", "assistant", and "system"

# Define Pydantic models for request and response data
class MessageSchema(BaseModel):
    content: str


class MessageRequestSchema(MessageSchema):
    role: str = "user"
    session_id: int


class AIMessageResponseSchema(MessageSchema):
    role: str = "assistant"
    session_id: int


class RawMessageRequestSchema(MessageSchema):
    # only used by the module `backend.utils.chat_completions_handler.get_openai_response`
    # without `session_id` parameter, compared to  `MessageRequestSchema` class
    role: str = "user"

class RawAIMessageResponseSchema(MessageSchema):
    # without `session_id` parameter, compared to `AIMessageResponseSchema` class
    role: str = "assistant"