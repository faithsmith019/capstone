import streamlit as st
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import Data.information as data

st.set_page_config(
    page_title="Login View",
    page_icon="🔐",
    layout="wide"
)

# Custom CSS to make the app fill the entire screen width
st.markdown("""
<style>
    .main .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .stApp {
        background-color: black;
    }
</style>
""", unsafe_allow_html=True)

init_db = st.session_state.get('init_db')
if not init_db:
    from Data.information import init_db
    init_db()
    st.session_state['init_db'] = True
    
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

# Initialize authenticator only once per user session to prevent
# duplicate Streamlit element keys (CookieManager uses a fixed
# 'init' key internally).  The app reruns on each interaction, so
# instantiating this object on every run caused the Streamlit
#DuplicateElementKey error.
if 'authenticator' not in st.session_state:
    st.session_state['authenticator'] = stauth.Authenticate(
        credentials,
        "maintenance_app",
        "abcdef",
        cookie_expiry_days=30,
    )
authenticator = st.session_state['authenticator']


# Show login UI only when not authenticated. Registration is moved to supervisor view.
authentication_status = st.session_state.get('authentication_status')
name = st.session_state.get('name')
username = st.session_state.get('username')

if not authentication_status:
    # Ensure stale view state doesn't persist while logged out
    for k in ('page', 'role'):
        st.session_state.pop(k, None)
    authenticator.login(location='main', key='Login')

# If authentication_status is None/False we'll still show messages below

# Ensure role is set in session state after login
role = st.session_state.get('role')
if authentication_status and username:
    credentials = load_credentials()
    role = credentials.get('usernames', {}).get(username, {}).get('role')
    if role:
        st.session_state['role'] = role
    else:
        st.session_state.pop('role', None)

role = st.session_state.get('role')

if authentication_status is False:
    st.error("Username/password is incorrect")
elif authentication_status is None:
    st.warning("Please enter your username and password. If you don't have one, please contact Res Life")

# Sidebar: show app nav and current role
with st.sidebar:
    st.title("Maintenance App")
    if authentication_status:
        st.write(f"Signed in as: *{name}*")
        st.write(f"Role: **{role or 'unknown'}**")
        # show the authenticator's logout control (this will clear cookies/session for stauth)
        authenticator.logout("Logout", "sidebar")
    else:
        st.write("Not signed in")
    st.header("Navigation")

    def nav_button(label, page_key):
        if st.button(label):
            st.session_state['page'] = page_key

    if authentication_status:
        if role == 'requestor':
            nav_button('Go to the Home Page', 'requestor')
        if role == 'supervisor':
            nav_button('Go to the Home Page', 'supervisor')
        if role == 'worker':
            nav_button('Go to the Home Page', 'worker')
    else:
        st.write('Log in to see navigation')

# If the user has been logged out (auth status not True) ensure we don't keep showing views
if not st.session_state.get('authentication_status'):
    # clear any view state left over
    for k in ('page', 'role', 'name', 'username'):
        st.session_state.pop(k, None)
    # avoid infinite rerun loops: only rerun if there is leftover UI state
    # This ensures after logout the app shows only the login UI
    #st.rerun()

# Render the selected view (views are in `views/` package so they don't show up in Streamlit's Pages menu)
page = st.session_state.get('page')
if not page and authentication_status:
    # default to role home and persist it so no sidebar click required
    page = role
    st.session_state['page'] = page
data.init_db()  # ensure DB is initialized before any view tries to use it
if page == 'requestor':
    from views.requestorview import render_requestor
    render_requestor()
elif page == 'worker':
    from views.workerview import render_worker
    render_worker()
elif page == 'supervisor':
    from views.supervisor import render_supervisor
    render_supervisor()
elif page == 'supervisor_view_upcoming':
    from views.supervisor import betterDisplayIncomingRequest
    if st.button("🏠 Back to Supervisor Home"):
        st.session_state['page'] = 'supervisor'
    betterDisplayIncomingRequest()
elif page == 'supervisor_view_past':
    from views.supervisor import showPastRequests
    if st.button("🏠 Back to Supervisor Home"):
        st.session_state['page'] = 'supervisor'
    showPastRequests()
elif page == 'supervisor_add_user':
    from views.supervisor import register_user
    if st.button("🏠 Back to Supervisor Home"):
        st.session_state['page'] = 'supervisor'
    register_user()
elif page == 'supervisor_edit_roles':
    from views.supervisor import edit_user_roles
    if st.button("🏠 Back to Supervisor Home"):
        st.session_state['page'] = 'supervisor'
    edit_user_roles()
elif page == 'maintenanceForm':
    # lazy-load the maintenance form only when requested
    from Controller.requestor import mainteanceForm
    if st.button("🏠 Back to Requestor Home"):
        st.session_state['page'] = 'requestor'
    mainteanceForm()
elif page == 'view_status':
    st.title("📋 View Status of Your Requests")
    if st.button("🏠 Back to Requestor Home"):
        st.session_state['page'] = 'requestor'
    st.write("This feature is coming soon! Here you will see the status of your submitted maintenance requests.")
elif page == 'edit_profile':
    st.title("👤 Edit Your Profile Information")
    if st.button("🏠 Back to Requestor Home"):
        st.session_state['page'] = 'requestor'
    st.write("This feature is coming soon! Here you can update your profile details.")
