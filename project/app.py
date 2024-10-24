import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from project.db_connection import get_db_session
from project.db_models import UserOrm
from project.schemas import UserRequestSchema

app = fastapi.FastAPI()


@app.get("/")
def get_root():
    return {"message": "Hello World, are you ok, why you are s..."}


async def check_user_exists(email: str, db: Session = Depends(get_db_session)):
    user_exists = db.query(UserOrm).filter(UserOrm.email == email).first()
    if user_exists:
        raise HTTPException(
            status_code=400, detail="User already exists with this email."
        )


@app.post("/api/v1/users")
async def register_user(user: UserRequestSchema, db: Session = Depends(get_db_session)):
    _ = await check_user_exists(user.email)
    user_orm = UserOrm(**user.dict())
    db.add(user_orm)
    db.commit()
    db.refresh(user_orm)
    return user_orm


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
