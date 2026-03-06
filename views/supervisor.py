import streamlit as st
from pathlib import Path
import pickle
import streamlit_authenticator as stauth
import sqlite3
from Data.information import init_db, add_user, add_maintenance_request


def render_supervisor():
    st.title("Supervisor View — User Role Management")

    if st.button("View upcoming requests"):
        showIncomingRequests()
    if st.button("View past requests"):
        showPastRequests()
    if st.button("Add user"):
        register_user()
    if st.button("Edit user roles"):
        edit_user_roles()
      

def register_user():
    st.header('Register a new user')
    with st.form('register_user'):
        new_username = st.text_input('Username')
        new_name = st.text_input('Full name')
        new_password = st.text_input('Password', type='password')
        new_role = st.selectbox('Role', ['requestor', 'supervisor', 'worker'])
        submitted = st.form_submit_button('Create user')
        if submitted:
            if not new_username or not new_password:
                st.error('Username and password are required')
            else:
                # hash the password using streamlit_authenticator helper
                try:
                    hashed = stauth.Hasher([new_password]).generate()[0]
                except Exception:
                    st.error('Unable to hash password (missing dependency?)')
                    hashed = new_password
                creds = load_credentials()
                creds.setdefault('usernames', {})[new_username] = {
                    'name': new_name or new_username,
                    'password': hashed,
                    'role': new_role,
                }
                save_credentials(creds)
                # drop existing authenticator so it will be recreated with the
                # new credentials on rerun.  This avoids using stale credential
                # data for subsequent logins.
                st.session_state.pop('authenticator', None)
                st.success(f'User {new_username} created with role {new_role}')
                st.rerun()
def load_credentials():
        CREDENTIALS_FILE = Path(__file__).parents[1] / 'hashed_pw.pkl'
        if CREDENTIALS_FILE.exists():
            with CREDENTIALS_FILE.open('rb') as f:
                return pickle.load(f)
        return {'usernames': {}}

def save_credentials(creds):
        CREDENTIALS_FILE = Path(__file__).parents[1] / 'hashed_pw.pkl'
        with CREDENTIALS_FILE.open('wb') as f:
            pickle.dump(creds, f)
def edit_user_roles():
    st.subheader("Edit User Roles")
    st.write("This section allows the supervisor to edit the roles of existing users in the system. You can change a user's role" \
    "to 'requestor', 'supervisor', or 'worker'.")
    #this function 

    creds = load_credentials()
    users = list(creds.get('usernames', {}).keys())
    if not users:
        st.info('No users found in credentials.')
        # still allow supervisor to create users even if none exist
        users = []

    st.write('Edit roles for existing users:')
    updated = False
    new_creds = creds.copy()
    for uname in users:
        info = creds['usernames'][uname]
        current = info.get('role', 'requestor')
        col1, col2 = st.columns([2,1])
        with col1:
            st.write(f"**{uname}** — {info.get('name')}")
        with col2:
            choice = st.selectbox(f"role_{uname}", ['requestor','supervisor','worker'], index=['requestor','supervisor','worker'].index(current))
            if choice != current:
                new_creds['usernames'][uname]['role'] = choice
                updated = True

    if updated and st.button('Save role changes'):
        save_credentials(new_creds)
        # refresh authenticator so role info or username/cred changes are
        # picked up by the login logic
        st.session_state.pop('authenticator', None)
        st.success('Roles updated')
        st.rerun()

def get_incoming_requests():
    """Fetch incoming maintenance requests from the database."""
    # central database lives in the Data package
    db_path = Path(__file__).parents[1] / "Data" / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, description, status, created_by, assigned_to,
               full_name, phone, date, building, apartment, location
        FROM maintenance_requests 
        WHERE status = 'open'
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    requests = []
    for row in rows:
        requests.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'status': row[3],
            'created_by': row[4],
            'assigned_to': row[5],
            'full_name': row[6],
            'phone': row[7],
            'date': row[8],
            'building': row[9],
            'apartment': row[10],
            'location': row[11]
        })
    return requests
def showIncomingRequests():
    st.subheader("Incoming Requests")
    st.write("This section will display all incoming maintenance requests for the supervisor to review and assign to workers.")
    incoming_requests = get_incoming_requests()  # This function should fetch requests from the database
    if incoming_requests:
        for req in incoming_requests:
            st.write(f"**Request ID:** {req['id']}")
            st.write(f"**Title:** {req['title']}")
            st.write(f"**Description:** {req['description']}")
            st.write(f"**Status:** {req['status']}")
            st.write(f"**Created By:** {req['created_by']}")
            st.write(f"**Assigned To:** {req['assigned_to']}")
            # show requestor details if available
            if req.get('full_name'):
                st.write(f"**Requestor:** {req['full_name']}")
            if req.get('phone'):
                st.write(f"**Phone:** {req['phone']}")
            if req.get('date'):
                st.write(f"**Date:** {req['date']}")
            if req.get('building') or req.get('apartment') or req.get('location'):
                loc = f"{req.get('building','')} {req.get('apartment','')} {req.get('location','')}".strip()
                st.write(f"**Location:** {loc}")
            st.write("---")
    else:
        st.info("No incoming requests at the moment.")

def showPastRequests():
    st.subheader("Past Requests")
    st.write("There are currently no past requests to show.")
    # central database lives in the Data package
    db_path = Path(__file__).parents[1] / "Data" / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, description, status, created_by, assigned_to,
               full_name, phone, date, building, apartment, location
        FROM maintenance_requests 
        WHERE status = 'closed' OR status = 'completed'
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    requests = []
    for row in rows:
        requests.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'status': row[3],
            'created_by': row[4],
            'assigned_to': row[5],
            'full_name': row[6],
            'phone': row[7],
            'date': row[8],
            'building': row[9],
            'apartment': row[10],
            'location': row[11]
        })
    return requests