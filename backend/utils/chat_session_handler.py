from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db_models import MessageOrm
import streamlit as st

async def load_previous_chat_session(session_id: int, db_session: AsyncSession) -> None:
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
        stmt = select(MessageOrm.role, MessageOrm.content).where(MessageOrm.session_id == session_id)
        result = await db_session.execute(stmt)
        all_messages = result.fetchall()

        st.session_state.messages = []
        for role, content in all_messages:
            st.session_state.messages.append({"role": role, "content": content})

    except SQLAlchemyError as error:
        st.error(f"Failed to load previous chat sessions: {error}")
        raise

    except Exception as error:
        st.error(f"Unexpected error occured: {error}")
        raise
