import passlib.hash
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db_connection import get_db_session
from backend.db_models import UserOrm
from backend.jwt_services import create_token, current_user
from backend.schemas.user_schemas import UserCreateSchema, UserResponseSchema
from backend.utils.user_handler import check_user_exists, login

users_router = APIRouter()


@users_router.post("/register", status_code=200)
async def register_user(
    user: UserCreateSchema, db_session: AsyncSession = Depends(get_db_session)
):
    try:
        _ = await check_user_exists(db_session, user)
        password_hash = passlib.hash.bcrypt.hash(user.password)

        user_obj = UserOrm(
            username=user.username,
            email=user.email,
            password_hash=password_hash,
        )
        db_session.add(user_obj)
        await db_session.commit()
        await db_session.refresh(user_obj)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    return await create_token(user_obj, db_session)


@users_router.post("/login", status_code=200)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db_session),
):
    db_user = await login(form_data.username, form_data.password, db_session)
    if not db_user:
        raise HTTPException(status_code=401, detail="Wrong login credentials.")
    # create token if user exists
    return await create_token(db_user, db_session)


@users_router.get("/current-user", response_model=UserResponseSchema)
async def current_user(user: UserResponseSchema = Depends(current_user)):
    return user
