from datetime import datetime


from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr


class UserCreateSchema(UserSchema):
    password: str


class UserRequestSchema(UserSchema):
    password: str


class UserResponseSchema(UserSchema):
    id: int
    created_at: datetime


class UserDeleteSchema(UserSchema):
    id: int
    user_role_id: int
    deleted_at: datetime
