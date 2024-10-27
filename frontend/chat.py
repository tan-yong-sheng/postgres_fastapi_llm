import os
from dataclasses import dataclass

import openai
import streamlit as st
from dotenv import find_dotenv, load_dotenv


_ = load_dotenv(find_dotenv())


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

if prompt:
    st.session_state[MESSAGES].append(Message(actor=USER, payload=prompt))
    st.chat_message(USER).write(prompt)

    with st.spinner("Please wait.."):
        chat_history = "\n".join(
            [f"{m.actor}: {m.payload}" for m in st.session_state[MESSAGES]]
        )
        response: str = get_openai_response(prompt, chat_history)
        st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=response))
        st.chat_message(ASSISTANT).write(response)
