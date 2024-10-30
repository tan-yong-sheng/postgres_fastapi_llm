from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, StringConstraints, UUID4


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
    id: UUID4
    created_at: datetime
    deleted_at: Optional[datetime] = None


class UserDeleteSchema(UserSchema):
    id: UUID4
    created_at: datetime
    deleted_at: datetime


