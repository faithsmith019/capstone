import streamlit as st
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

st.set_page_config(
    page_title="Login View",
    page_icon="🔐",
)

# Credentials file path
CREDENTIALS_FILE = Path(__file__).parent / "hashed_pw.pkl"

def infer_role_from_username(uname: str) -> str:
    u = (uname or "").lower()
    if 'requestor' in u:
        return 'requestor'
    if 'supervisor' in u or 'admin' in u:
        return 'supervisor'
    if 'worker' in u or 'staff' in u:
        return 'worker'
    return 'requestor'

def load_credentials():
    """Load credentials from pickle file."""
    if CREDENTIALS_FILE.exists():
        with CREDENTIALS_FILE.open("rb") as file:
            credentials = pickle.load(file)
            # Migrate: ensure every user has a role; save if we add roles
            changed = False
            if isinstance(credentials, dict) and 'usernames' in credentials:
                for uname, info in credentials['usernames'].items():
                    if isinstance(info, dict) and 'role' not in info:
                        info['role'] = infer_role_from_username(uname)
                        changed = True
            if changed:
                # persist migration
                with CREDENTIALS_FILE.open("wb") as out:
                    pickle.dump(credentials, out)
            return credentials
    return {"usernames": {}}

def save_credentials(credentials):
    """Save credentials to pickle file."""
    with CREDENTIALS_FILE.open("wb") as file:
        pickle.dump(credentials, file)

# Load initial credentials
credentials = load_credentials()

# Initialize authenticator
authenticator = stauth.Authenticate(
    credentials,
    "maintenance_app",
    "abcdef",
    cookie_expiry_days=30,
)

# Create login/register tabs w/ default authentication
tab1, tab2 = st.tabs(["Login", "Register"])
    
with tab1:
    authenticator.login(location='main', key='Login')

with tab2:
    # Register new user
    try:
        role = st.selectbox("Register as", ["requestor", "supervisor", "worker"])

        email_of_registered_user, username_of_registered_user, name_of_registered_user = (
            authenticator.register_user(
                location='main',
                pre_authorized=None,
                captcha=False,
            )
        )
        if email_of_registered_user:
            st.success(f"User {username_of_registered_user} registered successfully!")
            # Reload credentials from disk (register_user may have written them)
            credentials = load_credentials()
            # Attach role to the newly created user in credentials
            try:
                if 'usernames' in credentials and username_of_registered_user in credentials['usernames']:
                    credentials['usernames'][username_of_registered_user]['role'] = role
                else:
                    # Fallback: add the user entry with role if missing
                    credentials.setdefault('usernames', {})[username_of_registered_user] = {
                        'name': name_of_registered_user or username_of_registered_user,
                        'password': '',
                        'role': role,
                    }
            except Exception:
                pass
            # Save the newly registered user to credentials file
            save_credentials(credentials)
            st.info("You can now log in with your credentials.")
    except Exception as e:
        st.error(f"Error during registration: {e}")

# Read authentication state from Streamlit session state (login returns None when rendered)
name = st.session_state.get('name')
authentication_status = st.session_state.get('authentication_status')
username = st.session_state.get('username')

# Ensure role is set in session state after login
role = None
if authentication_status and username:
    # ensure we have the latest credentials from disk
    credentials = load_credentials()
    role = credentials.get('usernames', {}).get(username, {}).get('role')
    if role:
        st.session_state['role'] = role
    else:
        st.session_state.pop('role', None)

# expose local role var
role = st.session_state.get('role')

if authentication_status:
    st.write(f"Welcome *{name}*")
    st.write("You are now logged in.")
    
elif authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password")

# Sidebar: show app nav and current role
with st.sidebar:
    st.title("Maintenance App")
    if authentication_status:
        st.write(f"Signed in as: *{name}*")
        st.write(f"Role: **{role or 'unknown'}**")
        authenticator.logout("Logout", "sidebar")
    else:
        st.write("Not signed in")
    st.header("Navigation")
    # Role-aware navigation buttons
    def nav_button(label, page_key):
        if st.button(label):
            st.session_state['page'] = page_key

    if authentication_status:
        if role == 'requestor':
            nav_button('Go to Requestor View', 'requestor')
        if role == 'supervisor':
            nav_button('Go to Supervisor View', 'supervisor')
        if role == 'worker':
            nav_button('Go to Worker View', 'worker')
    else:
        st.write('Log in to see navigation')

# Render the selected view (views are in `views/` package so they don't show up in Streamlit's Pages menu)
page = st.session_state.get('page')
if not page and authentication_status:
    # default to role home
    page = role

if page == 'requestor':
    from views.requestorview import render as render_requestor
    render_requestor()
elif page == 'worker':
    from views.workerview import render as render_worker
    render_worker()
elif page == 'supervisor':
    from views.supervisor import render as render_supervisor
    render_supervisor()
