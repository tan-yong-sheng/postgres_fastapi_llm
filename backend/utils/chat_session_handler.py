from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db_models import MessageOrm, SessionOrm
from sqlalchemy.exc import SQLAlchemyError


# write another function which create a chat session...


async def load_all_chat_sessions(user_id, db_session: AsyncSession) -> list:
    try:
        stmt = select(SessionOrm.id, SessionOrm.start_timestamp, 
            SessionOrm.end_timestamp).where(
            (SessionOrm.user_id == user_id))
        result = await db_session.execute(stmt)
        all_sessions = result.fetchall()

        if not all_sessions:
            raise HTTPException(status_code=404, detail="No existing chat sessions found - are you a new user?")

        # Transform the results into a list of dictionaries
        all_sessions = [{"session_id": session_id,
                        "start_timestamp": start_timestamp,
                        "end_timestamp": end_timestamp} 
                        for session_id, start_timestamp, end_timestamp  in all_sessions]
        return all_sessions

    except SQLAlchemyError as e:
        raise HTTPException(status_code=404, detail=f"Failed to load previous chat sessions: {str(e)}")


async def load_previous_chats_in_session(session_id: int, user_id: int, db_session: AsyncSession) -> list:
    """
    Load messages of a previous chat session from the database and append to Streamlit's
    session state "messages".

    Args:
        session_id: The ID of the chat session to retrieve messages from.
        db_session: An asynchronous database session object.

    """
    try:
        stmt = select(MessageOrm.role, MessageOrm.content).where(
            (MessageOrm.session_id == session_id) & (MessageOrm.user_id == user_id))
        result = await db_session.execute(stmt)
        all_messages = result.fetchall()

        if not all_messages:
            raise HTTPException(status_code=404, detail="Chat session not found")

        # Transform the results into a list of dictionaries
        all_messages = [{"role": role, "content": content} for role, content in all_messages]
        return all_messages

    except SQLAlchemyError as e:
        raise HTTPException(status_code=404, detail=f"Failed to load previous chat messages for the session: {str(e)}")

    