import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv, find_dotenv

from config import settings
from schemas import RawMessageRequestSchema, RawAIMessageResponseSchema


_ = load_dotenv(find_dotenv())
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")


def display_messages():
    """Displays all messages from the session state."""
    for msg in st.session_state[settings.MESSAGES]:
        st.chat_message(msg.role).write(msg.content)


def add_user_message(prompt: str):
    """Adds a user's message to the session state and displays it."""
    st.session_state[settings.MESSAGES].append(RawMessageRequestSchema(role=settings.USER, content=prompt))
    st.chat_message(settings.USER).write(prompt)


def fetch_response(prompt: str, session_id: str) -> str:
    """Sends a prompt to the backend and retrieves the assistant's response."""
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/api/v1/chat/send-message",
            data=json.dumps({"content": prompt, "role": settings.USER, "session_id": session_id}),
            headers={'authorization': f"Bearer {st.session_state.access_token}"}
        )
        _ = response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error: {e}")
    except Exception as e:
        raise Exception(f"Internal server error: {e}")
    return str(response.json()["content"])


def add_assistant_message(response: str):
    """Adds the assistant's response to the session state and displays it."""
    st.session_state[settings.MESSAGES].append(RawAIMessageResponseSchema(role=settings.ASSISTANT, content=response))
    st.chat_message(settings.ASSISTANT).write(response)
