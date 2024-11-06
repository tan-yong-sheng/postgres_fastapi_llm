import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv, find_dotenv

from config import settings
from schemas import MessageSchema


_ = load_dotenv(find_dotenv())
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")


def _get_all_messages_in_chat_session(session_id: str) -> list[MessageSchema]:
    """
    Fetch and display chat messages for a given session_id.
    """
    try:
        url = f"{BACKEND_BASE_URL}/api/v1/chat/{session_id}"
        response = requests.get(
            url,
            headers={'authorization': f'Bearer {st.session_state.access_token}'}
        )
        _ = response.raise_for_status()
        message_list = response.json()
        return message_list
    except requests.exceptions.HTTPError as e:
        st.error(f"Failed to fetch messages: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")


# Bug: don't like how this write..., it should return in format of MessageSchema instead for consistency ...
def _fetch_assistant_response(prompt: str, session_id: str) -> str:
    """Sends a prompt to the backend and retrieves the assistant's response."""
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL}/api/v1/chat/new-message",
            data=json.dumps({"content": prompt, "role": settings.USER, "session_id": session_id}),
            headers={'authorization': f"Bearer {st.session_state.access_token}"}
        )
        _ = response.raise_for_status()
        return str(response.json()["content"])
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error: {e}")
    except Exception as e:
        raise Exception(f"Internal server error: {e}")
    


