import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from project.db_connection import get_db_session
from project.db_models import UserOrm
from project.schemas import UserCreateSchema

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
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error.")


async def create_token(user: UserOrm, db: Session):
    user_schema = UserSchema.model_validate(UserOrm)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
