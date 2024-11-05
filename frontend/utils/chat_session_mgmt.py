import os

import requests
import streamlit as st
from typing import Literal
from dotenv import load_dotenv, find_dotenv

from schemas import MessageSchema
from config import settings

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")


# Chat Session Management
def _create_new_chat_session():
    """Starts a new chat session by calling the backend API and returns the session ID."""
    try:
        url = f"{BACKEND_BASE_URL}/api/v1/chat/new-session"
        response = requests.post(
            url,
            headers={'authorization': f'Bearer {st.session_state.access_token}'}
        )
        response.raise_for_status()
        session_data = response.json()
        return session_data
    except requests.exceptions.HTTPError as e:
        raise Exception(f"HTTP error: {e}")
    except Exception as e:
        raise Exception(f"Internal server error: {e}")


def _get_all_chat_sessions():
    """Retrieve all chat sessions for the user."""
    url = f"{BACKEND_BASE_URL}/api/v1/chat/sessions"
    headers = {'Authorization': f'Bearer {st.session_state.access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


# Initialize Session State
def _initialize_session_state():
    """Initialize session state variables."""
    if "chat_sessions" not in st.session_state:
        st.session_state["chat_sessions"] = []
    if "active_chat_index" not in st.session_state:
        st.session_state["active_chat_index"] = 0
    if "messages" not in st.session_state:
        st.session_state["messages"] = []