import json
import os

import requests
import streamlit as st
from dotenv import find_dotenv, load_dotenv
from pydantic import EmailStr

_ = load_dotenv(find_dotenv())

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")

_ = st.header("Chat with LLM News App")

if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "access_token" not in st.session_state:
    st.session_state.jwt_token = ""


def login_user(username: str, password: str):
    """Fetches a JWT token from the FastAPI server."""
    url = f"{BACKEND_BASE_URL}/api/v1/login"
    response = requests.post(
        url,
        data={
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": None,
            "client_id": None,
            "client_secret": None,
        },
    )
    if response.status_code == 200:
        st.session_state.current_user = username
        st.session_state.access_token = response.json()["access_token"]
    else:
        print(f"Error fetching token: {response.status_code}")
        return None


def register_user(username: str, email: EmailStr, password: str):
    """Register a user with the FastAPI server."""
    url = f"{BACKEND_BASE_URL}/api/v1/users"
    response = requests.post(
        url,
        data=json.dumps(
            {
                "username": username,
                "email": email,
                "password": password,
            }
        ),
    )
    if response.status_code == 200:
        st.session_state.current_user = username
        st.session_state.access_token = response.json()["access_token"]
    else:
        st.warning(f"Error registering user: {response.json()}")
        return None


def authenticate_with_user():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login_user(username, password)
            st.rerun()

    with col2:
        st.subheader("Register")
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        if st.button("Register"):
            register_user(username, email, password)
            st.rerun()


def register_new_user():
    st.subheader("Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        register_user(username, email, password)
    st.rerun()


if not (st.session_state.current_user and st.session_state.access_token):
    _ = authenticate_with_user()
    st.stop()


navigation_tree = {
    "Main": [
        st.Page("home.py", title="Home", icon=":material/home:"),
        st.Page("news.py", title="News", icon=":material/newspaper:"),
        st.Page("chat.py", title="Chat", icon=":material/chat:"),
    ],
}

# get current user profile with JWT token
user = requests.get(
    f"{BACKEND_BASE_URL}/api/users/current-user",
    headers={"authorization": f"Bearer {st.session_state.access_token}"},
)
user_claims = user.json()

with st.sidebar:
    if st.button("Logout"):
        st.session_state.current_user = ""
        st.session_state.jwt_token = ""
        st.rerun()

nav = st.navigation(navigation_tree, position="sidebar")
nav.run()
