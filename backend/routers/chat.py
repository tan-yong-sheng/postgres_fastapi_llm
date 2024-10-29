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
from backend.schemas.chat_session_schemas import ChatSessionResponseSchema
from backend.utils.chat_completions_handler import get_openai_response
from backend.utils.chat_session_handler import (_get_all_chat_sessions, 
                                            _get_chat_history_by_session_id, 
                                            _create_new_chat_session)

chat_router = APIRouter()


@chat_router.get("/sessions", response_model = list[ChatSessionResponseSchema])
async def get_all_chat_sessions(user: UserResponseSchema=Depends(current_user), 
                                db_session: AsyncSession=Depends(get_db_session)):
    try:
        all_sessions = await _get_all_chat_sessions(user.id, db_session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    return all_sessions
        
@chat_router.get("/{session_id}", response_model = Optional[list[RawAIMessageResponseSchema]])
async def get_chat_history_by_session_id(session_id: int, 
                        user: UserResponseSchema = Depends(current_user),  
                        db_session: AsyncSession = Depends(get_db_session)):
    # get historical chat messages by session_id and user_id
    try:
        all_messages = await _get_chat_history_by_session_id(
                                session_id, user.id, db_session)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    return all_messages


@chat_router.post("/new-session")
async def create_new_chat_session(user: UserResponseSchema=Depends(current_user),
                            db_session: AsyncSession=Depends(get_db_session)):
    try:
        session_obj = await _create_new_chat_session(
                        user_id=user.id, db_session=db_session)
        return session_obj
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@chat_router.post("/send-message", response_model=AIMessageResponseSchema)
async def send_message(
    request: MessageRequestSchema,
    user: UserResponseSchema = Depends(current_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        messages_list = [{"role": request.role, "content": request.content}]
        if request.session_id:
            messages_list = await _get_chat_history_in_single_session(
                                request.session_id, user.id, db_session)
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
