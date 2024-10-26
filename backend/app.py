import os
from contextlib import asynccontextmanager

import fastapi
import openai
import passlib.hash
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import desc

from backend.db_connection import get_db_session
from backend.db_models import MessageOrm, SessionOrm, UserOrm
from backend.jwt_services import create_token, current_user
from backend.schemas.message_schemas import AIResponseSchema, MessageRequestSchema
from backend.schemas.user_schemas import UserCreateSchema, UserResponseSchema

_ = load_dotenv(find_dotenv())


# Create FastAPI app with lifespan
@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    # Startup
    yield
    # Shutdown


app = fastapi.FastAPI(lifespan=lifespan)


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


# not perfect as it's just combining the last 5 messages, and feed it to the model...
# The model doesn't know it's previous conversation
def get_openai_response(message: str, user_id: int) -> str:
    openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}],
        temperature=0.7,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        metadata={"user_id": user_id},
    )
    return response.choices[0].message.content


@app.post("/send_message", response_model=AIResponseSchema)
async def send_message(
    request: MessageRequestSchema,
    user: UserResponseSchema = Depends(current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        if request.session_id is None:
            # Manage session existence
            session_obj = SessionOrm(user_id=user.id)
            db_session.add(session_obj)
            await db_session.commit()
            # await db_session.refresh(session_obj)
            request.session_id = session_obj.id

        # Fetch the last 5 messages for context - helps maintain continuity
        stmt = (
            select(MessageOrm.user_id, MessageOrm.message)
            .where(MessageOrm.session_id == request.session_id)
            .order_by(desc(MessageOrm.created_at))
            .limit(5)
        )
        result = await db_session.execute(stmt)
        recent_messages = result.fetchall()

        # Building context from recent messages
        print(recent_messages)
        context = " ".join([message[1] for message in recent_messages])

        # Forming a context-rich prompt for the LLM
        full_prompt = f"{context} User: {request.message}"
        # Logging the conversation
        user_message_obj = MessageOrm(
            user_id=user.id,
            session_id=request.session_id,
            role="User",
            message=request.message,
        )
        db_session.add(user_message_obj)

        await db_session.commit()
        # await db_session.refresh(user_message_obj)

        ai_response = get_openai_response(full_prompt, user_id=user.id)
        AI_message_obj = MessageOrm(
            user_id=user.id,
            session_id=request.session_id,
            role="AI",
            message=ai_response,  # Corrected to use AI response
        )
        db_session.add(AI_message_obj)
        await db_session.commit()
        # await db_session.refresh(AI_message_obj)

        return AIResponseSchema(ai_response=ai_response, session_id=request.session_id)
    except HTTPException:
        raise
    except Exception as e:
        # Consider more specific exception handling and logging
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("__main__:app", host="0.0.0.0", port=8000, reload=True)
