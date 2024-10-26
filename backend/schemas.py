from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, StringConstraints


class UserSchema(BaseModel):
    username: Annotated[str, StringConstraints(min_length=1)]
    email: Annotated[EmailStr, StringConstraints(min_length=1)]


class UserCreateSchema(BaseModel):
    username: Annotated[str, StringConstraints(min_length=1)]
    email: Annotated[EmailStr, StringConstraints(min_length=1)]
    password: Annotated[str, StringConstraints(min_length=1)]


class UserRequestSchema(UserSchema):
    pass


class UserResponseSchema(UserSchema):
    id: int
    created_at: datetime
    deleted_at: Optional[datetime] = None


class UserDeleteSchema(UserSchema):
    id: int
    created_at: datetime
    deleted_at: datetime


# Define Pydantic models for request and response data
class MessageRequest(BaseModel):
    user_id: int
    session_id: Optional[int] = None
    message: str


# Define Pydantic models for request and response data
class AIResponse(BaseModel):
    ai_response: str
    session_id: Optional[int]
