from typing import Optional, Annotated
from enum import Enum
from pydantic import BaseModel, UUID4

class ChatActorEnum(str, Enum):
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'


# Define Pydantic models for request and response data
class MessageSchema(BaseModel):
    role: ChatActorEnum
    content: str


class MessageRequestSchema(MessageSchema):
    role: ChatActorEnum = ChatActorEnum.USER
    session_id: str


class AIMessageResponseSchema(MessageSchema):
    role: ChatActorEnum = ChatActorEnum.ASSISTANT
    session_id: str


class RawMessageRequestSchema(MessageSchema):
    # only used by the module `backend.utils.chat_completions_handler.get_openai_response`
    # without `session_id` parameter, compared to  `MessageRequestSchema` class
    role: str = ChatActorEnum.USER

class RawAIMessageResponseSchema(MessageSchema):
    # without `session_id` parameter, compared to `AIMessageResponseSchema` class
    role: str = ChatActorEnum.ASSISTANT