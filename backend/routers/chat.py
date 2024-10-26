from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import desc

from backend.db_connection import get_db_session
from backend.db_models import MessageOrm, SessionOrm
from backend.jwt_services import current_user
from backend.schemas.message_schemas import AIResponseSchema, MessageRequestSchema
from backend.schemas.user_schemas import UserResponseSchema
from backend.utils.openai_chat_handler import get_openai_response

chat_router = APIRouter()


# bug: need to break it down ...
@chat_router.post("/send-message", response_model=AIResponseSchema)
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
