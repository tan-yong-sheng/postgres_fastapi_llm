import streamlit as st
from dotenv import load_dotenv, find_dotenv
from config import settings
from utils.msg_mgmt import (display_messages,
                            add_user_message,
                            fetch_response,
                            add_assistant_message
                    )

def main(session_id: str):

    with st.sidebar:
        c1, c2 = st.columns(2)
        create_chat_button = c1.button(
            "新建", use_container_width=True, key="create_chat_button"
        )
        if create_chat_button:
            st.write("Hello, you clicked the button...")
            #st.rerun()

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