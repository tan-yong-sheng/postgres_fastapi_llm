import os
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv, find_dotenv

from config import settings
from schemas import MessageSchema, RawAIMessageResponseSchema, RawMessageRequestSchema
from utils.msg_mgmt import (_fetch_assistant_response, 
                            _get_all_messages_in_chat_session)
from utils.chat_session_mgmt import (_initialize_session_state, 
                                    _create_new_chat_session,
                                    _get_all_chat_sessions)

# Load environment variables
_ = load_dotenv(find_dotenv())
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")


def create_new_chat_session_in_ui():
    """Adds a new chat session to the chat history and sets it as the active chat."""
    session_data = _create_new_chat_session()
    new_chat_name = f"New Chat_{session_data['session_id']}"
    st.session_state["chat_sessions"].insert(0, new_chat_name)
    st.session_state["active_chat_index"] = 0

# BUG Comment: we don't have the endpoint to delete chat session yet...
def remove_current_chat_in_ui():
    """Removes the currently selected chat from the session history."""
    if len(st.session_state["chat_sessions"]) > 1:
        current_chat = st.session_state["chat_sessions"][st.session_state["active_chat_index"]]
        st.session_state["chat_sessions"].remove(current_chat)
        st.session_state["active_chat_index"] = max(0, st.session_state["active_chat_index"] - 1)


def add_user_message_to_ui(prompt: str):
    """Adds a user's message to the session state and displays it."""
    st.session_state[settings.MESSAGES].append(RawMessageRequestSchema(role=settings.USER, content=prompt))
    st.chat_message(settings.USER).write(prompt)


def add_assistant_message_to_ui(response: str):
    """Adds the assistant's response to the session state and displays it."""
    st.session_state[settings.MESSAGES].append(RawAIMessageResponseSchema(role=settings.ASSISTANT, content=response))
    st.chat_message(settings.ASSISTANT).write(response)


def display_chat_sessions_to_ui(user_id):
    return _get_all_chat_sessions()


def display_messages_to_ui(messages: list[MessageSchema]):
    """
    Fetch and display chat messages for a given session_id.
    """
    # Display each message in the chat history
    for message in messages:
        st.chat_message(message["role"]).write(message['content'])


def main():
    # Initialize chat session state
    _ = _initialize_session_state()

    # Sidebar for chat session management
    with st.sidebar:
        st.title("Chat Sessions")

        # Button to start a new chat session
        if st.button("Start New Chat"):
            _ = create_new_chat_session_in_ui()

        # List of existing chat sessions
        for i, chat_name in enumerate(st.session_state["chat_sessions"]):
            if st.button(chat_name, key=f"chat_{i}"):
                st.session_state["active_chat_index"] = i

        # Button to delete the currently selected chat
        if st.session_state["chat_sessions"]:
            if st.button("Delete Chat"):
                _ = remove_current_chat_in_ui()

    # Set the current chat session ID
    if st.session_state["chat_sessions"]:
        active_chat_name = st.session_state["chat_sessions"][st.session_state["active_chat_index"]]
        session_id = active_chat_name.split("_")[-1]  # Extract session ID from chat name
    else:
        # BUG: need to create session_id here
        session_id = None 

    # Display chat messages
    messages_list = _get_all_messages_in_chat_session(session_id)
    _ = display_messages_to_ui(messages_list)

    # User input for new messages
    user_input = st.chat_input("Enter your message here")
    if user_input:
        _ = add_user_message_to_ui(user_input)
        with st.spinner("Processing response..."):
            ai_response = _fetch_assistant_response(user_input, session_id)
            _ = add_assistant_message_to_ui(ai_response)


_ = main()