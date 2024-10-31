import os
import requests
import streamlit as st
from dotenv import load_dotenv, find_dotenv

from config import settings
from utils.msg_mgmt import (display_messages,
                            add_user_message,
                            fetch_response,
                            add_assistant_message
                    )

_ = load_dotenv(find_dotenv())
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")


def create_new_chat_session():
    try:
        url = f"{BACKEND_BASE_URL}/api/v1/chat/new-session"
        response = requests.post(url, 
            headers={'authorization': f'Bearer {st.session_state.access_token}'})
        _ = response.raise_for_status()
        session_obj = response.json()
        return session_obj
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error: {e}")
    except Exception as e:
        raise Exception(f"Internal server error: {e}")

def create_chat_fun():
    st.session_state["history_chats"] = [
        "New Chat_" + str(uuid.uuid4())
    ] + st.session_state["history_chats"]
    st.session_state["current_chat_index"] = 0


def delete_chat_fun():
    if len(st.session_state["history_chats"]) == 1:
        chat_init = "New Chat_" + str(uuid.uuid4())
        st.session_state["history_chats"].append(chat_init)
    pre_chat_index = st.session_state["history_chats"].index(current_chat)
    if pre_chat_index > 0:
        st.session_state["current_chat_index"] = (
            st.session_state["history_chats"].index(current_chat) - 1
        )
    else:
        st.session_state["current_chat_index"] = 0
    st.session_state["history_chats"].remove(current_chat)
    remove_data(st.session_state["path"], current_chat)




def main(session_id: str):

    with st.sidebar:
        c1, c2 = st.columns(2)
        create_chat_button = c1.button(
            "New chat", use_container_width=True, key="create_chat_button"
        )
        if create_chat_button:
            session_obj = create_new_chat_session()
            st.write(session_obj)
            # st.write("Hello, you clicked the button...")
            # st.rerun()

    # Initialize messages in session state if not already done
    if settings.MESSAGES not in st.session_state:
        st.session_state[settings.MESSAGES] = []

    display_messages()

    # Get user input
    prompt = st.chat_input("Enter a prompt here")

    # Process the user's prompt if it exists
    if prompt:
        _ = add_user_message(prompt)

        # Show loading spinner while processing
        with st.spinner("Please wait.."):
            ai_response = fetch_response(prompt, session_id)
            _ = add_assistant_message(ai_response)


# Example usage: replace 'session_id' with your actual session identifier
session_id = "00e698ee-0870-4faf-b18d-68dc141f591a"  # Replace with dynamic session ID handling as needed
main(session_id)