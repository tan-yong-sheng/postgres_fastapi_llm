import os
import json
import streamlit as st

from utils.user_mgmt import _login_user, _register_user


_ = st.header("Chat with LLM News App")

if "current_user" not in st.session_state:
    st.session_state.current_user = ""
if "access_token" not in st.session_state:
    st.session_state.jwt_token = ""


def authenticate_with_user_view():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            _ = _login_user(username, password)
            st.rerun()

    with col2:
        st.subheader("Register")
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        if st.button("Register"):
            _ = _register_user(username, email, password)
            st.rerun()

if not (st.session_state.current_user and st.session_state.access_token):
    _ = authenticate_with_user_view()
    st.stop()


navigation_tree = {
    "Main": [
        st.Page("news_view.py", title="News", icon=":material/newspaper:"),
        st.Page("chat_view.py", title="Chat", icon=":material/chat:"),
    ],
}

# get current user profile with JWT token
#user = requests.get(
#    f"{BACKEND_BASE_URL}/api/v1/users/current-user",
#    headers={"authorization": f"Bearer {st.session_state.access_token}"},
#)
#user_claims = user.json()

#with st.topbar:
#    if st.button("Logout"):
#        st.session_state.current_user = ""
#        st.session_state.jwt_token = ""
#        st.rerun()

nav = st.navigation(navigation_tree, position="sidebar", expanded=False)
nav.run()
