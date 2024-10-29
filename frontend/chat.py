import os
from dataclasses import dataclass
import requests
import json

import openai
import streamlit as st
from dotenv import find_dotenv, load_dotenv


_ = load_dotenv(find_dotenv())

session_id = 1 # can try to call API via ``
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")

@dataclass
class Message:
    actor: str
    payload: str


USER = "user"
ASSISTANT = "ai"
MESSAGES = "messages"

def initialize_session_state():
    if MESSAGES not in st.session_state:
        st.session_state[MESSAGES] = [
            Message(actor=ASSISTANT, payload="Hi! How can I help you?")
        ]


initialize_session_state()

msg: Message
for msg in st.session_state[MESSAGES]:
    st.chat_message(msg.actor).write(msg.payload)

prompt: str = st.chat_input("Enter a prompt here")

# Bug: don't create session_id or continue to certain session..
if prompt:
    st.session_state[MESSAGES].append(Message(actor=USER, payload=prompt))
    st.chat_message(USER).write(prompt)

    with st.spinner("Please wait.."):
        chat_history = "\n".join(
            [f"{m.actor}: {m.payload}" for m in st.session_state[MESSAGES]]
        )
        response: str = requests.post(f"{BACKEND_BASE_URL}/api/v1/chat/send-message", 
                                    data=json.dumps({
                                            "content": prompt,
                                            "role": "user",
                                            "session_id": session_id
                                            }),
                                    headers={'authorization': f"Bearer {st.session_state.access_token}"})
        _ = response.raise_for_status()
        ai_response = str(response.json()["content"])
        st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=ai_response))
        st.chat_message(ASSISTANT).write(ai_response)
