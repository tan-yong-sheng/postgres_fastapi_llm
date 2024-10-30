import streamlit as st
from typing import Literal

from schemas import MessageSchema
from config import settings


def initialize_session_state():
    if MESSAGES not in st.session_state:
        st.session_state[settings.MESSAGES] = [
            MessageSchema(role=settings.ASSISTANT, payload="Hi! How can I help you?")
        ]

