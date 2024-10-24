import fastapi
from fastapi import Depends
from sqlalchemy.orm import Session

from project.db_connection import get_db_session
from project.schemas import UserRequestSchema

app = fastapi.FastAPI()


@app.get("/")
def get_root():
    return {"message": "Hello World, are you ok, why you are s..."}


@app.get("/api/v1/users")
async def register_user(user: UserRequestSchema, db: Session = Depends(get_db_session)):
    return {"message": "User registered successfully!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
