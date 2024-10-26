import requests
import streamlit as st
from pydantic import EmailStr

st.header("Chat with LLM News App")


BASE_URL = "http://localhost:8000"
SECRET_KEY = "secret"
ALGORITHM = "HS256"

if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "access_token" not in st.session_state:
    st.session_state.jwt_token = ""


def login_user(username: str, password: str):
    """Fetches a JWT token from the FastAPI server."""
    url = f"{BASE_URL}/api/v1/login"
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
    url = f"{BASE_URL}/api/v1/register"
    response = requests.post(
        url,
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    if response.status_code == 200:
        st.session_state.current_user = username
        st.session_state.access_token = response.json()["access_token"]
    else:
        print(f"Error registering user: {response.status_code}")
        return None


def authenticate_with_user():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login_user(username, password)
    st.rerun()


# def register_new_user():
#    st.subheader("Register")
#    username = st.text_input("Username")
#    email = st.text_input("Email")
#    password = st.text_input("Password", type="password")
#    if st.button("Register"):
#        register_user(username, email, password)
#    st.rerun()


if not (st.session_state.current_user and st.session_state.access_token):
    _ = authenticate_with_user()
    st.stop()


navigation_tree = {
    "Main": [
        st.Page("home.py", title="Home", icon=":material/home:"),
    ],
}
