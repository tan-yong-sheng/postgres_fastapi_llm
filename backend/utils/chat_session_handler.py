from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db_models import MessageOrm
from sqlalchemy.exc import SQLAlchemyError

async def load_previous_chat_session(session_id: int, user_id: int, db_session: AsyncSession) -> list:
    """
    Load messages of a previous chat session from the database and append to Streamlit's
    session state "messages".

    Args:
        session_id: The ID of the chat session to retrieve messages from.
        db_session: An asynchronous database session object.

    Returns:
        None. Messages are loaded into `st.session_state.messages`.
    """
    try:
        stmt = select(MessageOrm.role, MessageOrm.content).where(
            (MessageOrm.session_id == session_id) & (MessageOrm.user_id == user_id))
        result = await db_session.execute(stmt)
        all_messages = result.fetchall()

        if not all_messages:
            return

        return all_messages

    except SQLAlchemyError as error:
        raise Exception(f"Failed to load previous chat sessions: {error}")

    except Exception as error:
        raise Exception(f"Unexpected error occured: {error}")

    