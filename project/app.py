import fastapi
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.orm import Session

from project.db_connection import get_db_session
from project.db_models import UserOrm
from project.jwt_services import create_token, current_user
from project.schemas import UserCreateSchema

_ = load_dotenv(find_dotenv())
app = fastapi.FastAPI()


async def check_user_exists(
    db: Session,
    user: UserCreateSchema,
) -> None:
    existing_user = (
        db.query(UserOrm)
        .filter((UserOrm.email == user.email) | (UserOrm.username == user.username))
        .first()
    )
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
async def register_user(user: UserCreateSchema, db: Session = Depends(get_db_session)):
    import passlib.hash

    try:
        _ = await check_user_exists(db, user)
        password_hash = passlib.hash.bcrypt.hash(user.password)
        user_obj = UserOrm(
            username=user.username, email=user.email, password_hash=password_hash
        )
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}: Internal server error.")
    return await create_token(user_obj, db)


async def get_user_by_email(email: EmailStr, db: Session) -> UserOrm:
    return db.query(UserOrm).filter(UserOrm.email == email).first()


async def login(email: str, password: str, db: Session = Depends(get_db_session)):
    db_user = await get_user_by_email(email, db)
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
    db: Session = Depends(get_db_session),
):
    db_user = await login(form_data.username, form_data.password, db)
    if not db_user:
        raise HTTPException(status_code=401, detail="Wrong login credentials.")
    # create token if user exists
    return await create_token(db_user, db)


@app.get("/api/users/current-user")
async def get_home(auth=Depends(current_user)):
    return {"message": "Hello, World!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
