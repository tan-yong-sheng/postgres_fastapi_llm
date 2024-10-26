from contextlib import asynccontextmanager

import fastapi
from dotenv import find_dotenv, load_dotenv

from backend.routers.chat import chat_router
from backend.routers.user import users_router

_ = load_dotenv(find_dotenv())


# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    # Startup
    yield
    # Shutdown


app = fastapi.FastAPI(lifespan=lifespan)
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
