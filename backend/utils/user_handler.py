from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.db_connection import get_db_session
from backend.db_models import UserOrm
from backend.schemas.user_schemas import UserCreateSchema


async def check_user_exists(
    db_session: AsyncSession,
    user: UserCreateSchema,
) -> None:
    stmt = select(UserOrm).where(UserOrm.username == user.username)
    result = await db_session.execute(stmt)
    existing_user = result.scalars().first()

    if existing_user:
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=400, detail="Email already exists with this email."
            )
        elif existing_user.username == user.username:
            raise HTTPException(
                status_code=400, detail="Username already exists with this email."
            )
    return existing_user


async def get_user_by_username(username: str, db_session: AsyncSession) -> UserOrm:
    # get user by email or username
    stmt = select(UserOrm).where(UserOrm.username == username)
    result = await db_session.execute(stmt)
    return result.scalars().first()


async def login(
    username: str, password: str, db_session: AsyncSession = Depends(get_db_session)
):
    db_user = await get_user_by_username(username, db_session)
    # return false if no user with email found
    if not db_user:
        return False
    # return false if no user with password found
    if not db_user.password_verification(password):
        return False
    return db_user
