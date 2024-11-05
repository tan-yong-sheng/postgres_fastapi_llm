import os
import json
import streamlit as st
import requests
from pydantic import EmailStr
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL")

def _login_user(username: str, password: str):
    """Fetches a JWT token from the FastAPI server."""
    url = f"{BACKEND_BASE_URL}/api/v1/users/login"
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


def _register_user(username: str, email: EmailStr, password: str):
    """Register a user with the FastAPI server."""
    url = f"{BACKEND_BASE_URL}/api/v1/users/register"
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
