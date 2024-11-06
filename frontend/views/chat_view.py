import os
from typing import Optional
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
session_id: str = ""


def create_new_chat_session_in_ui():
    """Adds a new chat session to the chat history and sets it as the active chat."""
    session_data = _create_new_chat_session()
    # update session_id for current chat session
    st.session_state["chat_session"] = {"session_id": session_data["session_id"]}
    # add new chat session, and append the new chat sessions to sessions_history
    new_chat_name = f"New Chat_{session_data['session_id']}"
    st.session_state["sessions_history"].insert(0, new_chat_name)


def add_user_message_to_ui(prompt: str):
    """Adds a user's message to the session state and displays it."""
    message = RawMessageRequestSchema(role="user", content=prompt)
    st.session_state["messages"].append(message)
    with st.chat_message("user"):
        st.write(prompt)


def add_assistant_message_to_ui(response: str):
    """Adds the assistant's response to the session state and displays it."""
    message = RawAIMessageResponseSchema(role="assistant", content=response)
    st.session_state["messages"].append(message)
    with st.chat_message("assistant"):
        st.write(response)


def display_historical_messages_to_ui(messages: list[MessageSchema]):
    """
    Fetch and display chat messages for a given session_id.
    """
    for message in messages:
        with st.chat_message(message["role"]):
            st.write(message['content'])


# Not working yet...
def display_chat_sessions_to_ui():    
    # sessions_data = _get_all_chat_sessions()
    if "sessions_history" in st.session_state:
        # BUG -- ...
        # try to retrieve all chat sessions from streamlit's session_state...
        session_list = st.session_state["sessions_history"]
        print("======2")
        print(session_list)
        for session_id in session_list:
            chat_name = f"New Chat_{session_id}"
            # Display each chat session button
            with st.sidebar:
                for i, chat_name in enumerate(st.session_state["sessions_history"]):
                    _ = st.button(chat_name, key=f"chat_{i}")    
                    #st.session_state["active_chat_index"] = i


def main():
    # Initialize chat session state if not already done
    _ = _initialize_session_state()

    # Sidebar for chat session management
    with st.sidebar:
        st.title("Chat Sessions")

        # Button to start a new chat session
        if st.button("Start New Chat"):
            _ = create_new_chat_session_in_ui()

    # Create new chat session in streamlit
    ## check if there is any existing session_id
    if "chat_session" in st.session_state:
        session_id = st.session_state["chat_session"].get("session_id", None)
        if session_id:
            messages_list = _get_all_messages_in_chat_session(session_id)
            _ = display_historical_messages_to_ui(messages_list)

    if "sessions_history" in st.session_state:
        pass
        #_ = display_chat_sessions_to_ui()

    # User input for new messages (without creating new sessions on submit)
    user_input = st.chat_input("Enter your message here")
    if user_input:
        add_user_message_to_ui(user_input)
        with st.spinner("Processing response..."):
            session_id = st.session_state["chat_session"].get("session_id")
            ai_response = _fetch_assistant_response(user_input, session_id)
            add_assistant_message_to_ui(ai_response)

_ = main()
