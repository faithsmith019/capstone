import streamlit as st
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

# Login authentication setup
names = ["John Doe", "Jane Smith"]
usernames = ["johndoe", "janesmith"]

# Load hashed passwords and build credentials dict expected by streamlit_authenticator
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

# `streamlit_authenticator` expects a credentials dict with the shape:
# {"usernames": {"username": {"name": "Full Name", "password": "<hash>"}, ...}}
if isinstance(hashed_passwords, list):
    credentials = {"usernames": {}}
    for uname, nm, pw in zip(usernames, names, hashed_passwords):
        credentials["usernames"][uname] = {"name": nm, "password": pw}
else:
    # If the pickle already contains a credentials-like dict, use it directly
    credentials = hashed_passwords

authenticator = stauth.Authenticate(
    credentials,
    "maintenance_app",
    "abcdef",
    cookie_expiry_days=30,
)

authenticator.login(location='main', key='Login')

# Read authentication state from Streamlit session state (login returns None when rendered)
name = st.session_state.get('name')
authentication_status = st.session_state.get('authentication_status')
username = st.session_state.get('username')

if authentication_status:
    st.write(f"Welcome *{name}*")
    authenticator.logout("Logout", "main")
    st.write("You are now logged in.")
    
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")



st.set_page_config(
    page_title = "Login View",
    page_icon = "🔐",)

