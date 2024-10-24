from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    user_role_id: int
    password_hash: str
    created_at: datetime


class UserRequestSchema(UserSchema):
    password: str


class UserResponseSchema(UserSchema):
    id: int


class UserDeleteSchema(UserSchema):
    id: int
    deleted_at: datetime
