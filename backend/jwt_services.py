import os

import jwt
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.db_connection import get_db_session
from backend.db_models import UserOrm
from backend.schemas.user_schemas import UserResponseSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

_ = load_dotenv(find_dotenv())


async def create_token(user: UserOrm, db_session: AsyncSession):
    user_schema = UserResponseSchema.model_validate(user.__dict__)
    user_dict = dict(user_schema)
    del user_dict["created_at"]
    token = jwt.encode(user_dict, os.getenv("_JWT_SECRET_KEY"))
    return dict(access_token=token, token_type="bearer")


async def current_user(
    db_session: AsyncSession = Depends(get_db_session),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload = jwt.decode(token, os.getenv("_JWT_SECRET_KEY"), algorithms=["HS256"])
        # get user by Id is already available in the decoded user payload along with the token
        stmt = select(UserOrm).filter(UserOrm.id == payload["id"])
        result = await db_session.execute(stmt)
        db_user = result.scalars().first()
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"{e}: wrong credentials")
    return db_user
