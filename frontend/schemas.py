
from enum import Enum
from pydantic import BaseModel

class ChatActorEnum(str, Enum):
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'

class MessageSchema(BaseModel):
    role: ChatActorEnum
    content: str


class RawMessageRequestSchema(MessageSchema):
    role: ChatActorEnum = ChatActorEnum.USER


class RawAIMessageResponseSchema(MessageSchema):
    role: ChatActorEnum = ChatActorEnum.ASSISTANT