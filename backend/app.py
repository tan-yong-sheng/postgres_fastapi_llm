import fastapi
import passlib.hash
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.db_connection import get_db_session
from backend.db_models import UserOrm
from backend.jwt_services import create_token, current_user
from backend.schemas import UserCreateSchema, UserResponseSchema

_ = load_dotenv(find_dotenv())
app = fastapi.FastAPI()


async def check_user_exists(
    db_session: AsyncSession,
    user: UserCreateSchema,
) -> None:
    stmt = select(UserOrm).filter(UserOrm.username == user.username)
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


@app.post("/api/v1/users", status_code=200)
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
        raise HTTPException(status_code=500, detail=f"{e}: Internal server error.")

    return await create_token(user_obj, db_session)


async def get_user_by_username(username: str, db_session: AsyncSession) -> UserOrm:
    # get user by email or username
    stmt = select(UserOrm).filter(UserOrm.username == username)
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


@app.post("/api/v1/login", status_code=200)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db_session),
):
    db_user = await login(form_data.username, form_data.password, db_session)
    if not db_user:
        raise HTTPException(status_code=401, detail="Wrong login credentials.")
    # create token if user exists
    return await create_token(db_user, db_session)


@app.get("/api/users/current-user", response_model=UserResponseSchema)
async def current_user(user: UserResponseSchema = Depends(current_user)):
    return user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
