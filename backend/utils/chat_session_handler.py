from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import asyncpg  # Import specific asyncpg error
from backend.db_models import MessageOrm, SessionOrm
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.sql import asc, desc

async def _create_new_chat_session(user_id: int, db_session: AsyncSession):
    try:
        session_obj = SessionOrm(user_id=user_id)
        db_session.add(session_obj)
        await db_session.commit()
        await db_session.refresh(session_obj)
        return session_obj
    except SQLAlchemyError as e:
        raise HTTPException(status_code=404, detail=f"Failed to create a new chat session: {str(e)}")
    

async def _get_all_chat_sessions(user_id: int, db_session: AsyncSession) -> list:
    try:
        stmt = select(SessionOrm.id, SessionOrm.user_id, 
                    SessionOrm.start_timestamp, 
                    ).where(
                    (SessionOrm.user_id == user_id)
                    ).order_by(desc(SessionOrm.start_timestamp))
        result = await db_session.execute(stmt)
        all_sessions = result.fetchall()

        if not all_sessions:
            raise HTTPException(status_code=404, 
                detail="No existing chat sessions found - are you a new user?")

        # Transform the results into a list of dictionaries
        all_sessions = [{"session_id": session[0],
                        "user_id": session[1],
                        "start_timestamp": session[2],
                        } 
                        for session in all_sessions]
        return all_sessions

    except SQLAlchemyError as e:
        raise HTTPException(status_code=404, detail=f"Failed to load previous chat sessions: {str(e)}")

async def _check_existing_chat_session(session_id: int, user_id: int, db_session: AsyncSession):
    try:
        stmt = select(SessionOrm.id, SessionOrm.user_id, 
                    SessionOrm.start_timestamp,
                    ).where(
                    ((SessionOrm.user_id == user_id) & (SessionOrm.id == session_id)))
        result = await db_session.execute(stmt)
        chat_session = result.scalars().first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="No chat session found. Please double check the session_id for the chat.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=404, detail=f"No chat session found. Please double check the session_id for the chat: {str(e)}")


async def _get_chat_history_by_session_id(session_id: int, user_id: int, db_session: AsyncSession) -> list:
    """
    Load messages of a previous chat session from the database and append to Streamlit's
    session state "messages".

    Args:
        session_id: The ID of the chat session to retrieve messages from.
        db_session: An asynchronous database session object.

    """
    try:
        _ = await _check_existing_chat_session(session_id, user_id, db_session)

        stmt = select(MessageOrm.role, MessageOrm.content).where(
            (MessageOrm.session_id == session_id) & (MessageOrm.user_id == user_id)
            ).order_by(asc(MessageOrm.created_at))
        result = await db_session.execute(stmt)
        all_messages = result.fetchall()
        # Transform the results into a list of dictionaries
        if not all_messages:
            return []
        all_messages = [{"role": message[0], "content": message[1]} for message in all_messages]
        return all_messages
    except SQLAlchemyError as e:
        raise HTTPException(status_code=404, detail=f"Failed to load previous chat messages for the session: {str(e)}")

    