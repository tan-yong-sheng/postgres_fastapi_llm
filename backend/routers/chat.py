from typing import Optional, Union
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import desc

from backend.db_connection import get_db_session
from backend.db_models import MessageOrm, SessionOrm
from backend.jwt_services import current_user
from backend.schemas.message_schemas import AIMessageResponseSchema, MessageRequestSchema, RawAIMessageResponseSchema
from backend.schemas.user_schemas import UserResponseSchema
from backend.utils.chat_completions_handler import get_openai_response
from backend.utils.chat_session_handler import load_all_chat_sessions, load_previous_chats_in_session

chat_router = APIRouter()

@chat_router.post("/create-session")
async def create_chat_session():
    pass

@chat_router.get("/sessions")
async def get_all_chat_sessions(user: UserResponseSchema=Depends(current_user), 
                                db_session: AsyncSession = Depends(get_db_session)):
    try:
        all_sessions = await load_all_chat_sessions(user.id, db_session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    return all_sessions
        
@chat_router.get("/{session_id}", response_model = Optional[list[RawAIMessageResponseSchema]])
async def get_chat_history_in_single_session(session_id: int, 
                        user: UserResponseSchema = Depends(current_user),  
                        db_session: AsyncSession = Depends(get_db_session)):
    # get historical chat messages by session_id and user_id
    try:
        all_messages = await load_previous_chats_in_session(session_id, user.id, db_session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    return all_messages

# bug: need to break it down ...
@chat_router.post("/send-message", response_model=AIMessageResponseSchema)
async def send_message(
    request: MessageRequestSchema,
    user: UserResponseSchema = Depends(current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        messages_list = [{"role": request.role, "content": request.content}]
        if request.session_id is None:
            # Manage session existence
            session_obj = SessionOrm(user_id=user.id)
            db_session.add(session_obj)
            await db_session.commit()
            # await db_session.refresh(session_obj)
            request.session_id = session_obj.id
        else:
            messages_list = await load_previous_chats_in_session(request.session_id, user.id, db_session)
            messages_list.append({"role": request.role, "content": request.content})

        # Logging the conversation
        user_message_obj = MessageOrm(
            user_id=user.id,
            session_id=request.session_id,
            role=request.role,
            content=request.content,
        )
        db_session.add(user_message_obj)
        await db_session.commit()

        ai_response = get_openai_response(messages_list, user_id=user.id)
        AI_message_obj = MessageOrm(
            user_id=user.id,
            session_id=request.session_id,
            role=ai_response.role,
            content=ai_response.content,
        )
        db_session.add(AI_message_obj)
        await db_session.commit()

        return AIMessageResponseSchema(
                                content=ai_response.content,
                                role=ai_response.role,
                                session_id=request.session_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
