import requests
import streamlit as st
from pathlib import Path
import pickle
import streamlit_authenticator as stauth
import sqlite3
from Data.information import init_db, add_user, add_maintenance_request


def render_supervisor():
    st.title("👔 Supervisor Dashboard")
    st.write("Manage maintenance requests and user roles.")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        if st.button("📋 View Upcoming Requests", use_container_width=True):
            st.session_state['page'] = 'supervisor_view_upcoming'

    with col2:
        if st.button("📚 View Past Requests", use_container_width=True):
            st.session_state['page'] = 'supervisor_view_past'

    with col3:
        if st.button("👤 Add New User", use_container_width=True):
            st.session_state['page'] = 'supervisor_add_user'

    with col4:
        if st.button("🔧 Edit User Roles", use_container_width=True):
            st.session_state['page'] = 'supervisor_edit_roles'
      

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

def betterDisplayIncomingRequest():
    # load incoming requests
    requests = get_requests()
    
    # Display messages at the top
    if "error_msg" in st.session_state:
        st.error(st.session_state["error_msg"])
        del st.session_state["error_msg"]
    if "success_msg" in st.session_state:
        st.success(st.session_state["success_msg"])
        del st.session_state["success_msg"]
    
    selected_ids = st.session_state.get("selected_ids", [])
    
    checked_ids = []
    
    action = None
    
    # Top row: Filter, Select All, Approve, Reject
    top_col1, top_col2, top_col3 = st.columns([0.2, 0.2, 0.6])
    with top_col1:
        status_filter = st.selectbox("Filter Status", ["All","open","approved","rejected"])
    with top_col2:
        select_all = st.checkbox("Select All", key="select_all")
    with top_col3:
        button_cols = st.columns(2)
        with button_cols[0]:
            if st.button("Approve Selected"):
                action = 'approve'
        with button_cols[1]:
            if st.button("Reject Selected"):
                action = 'reject'
    
    filtered = [
        r for r in requests
        if (status_filter=="All" or r["status"]==status_filter)
    ]
    
    if select_all:
        selected_ids = [r['id'] for r in filtered]
    
    checked_ids = []
    
    # Columns: List + Details (pushed details to the right)
    list_col, detail_col = st.columns([2.5, 1.5])
    
    # Track selected request
    if "selected_request" not in st.session_state:
        st.session_state["selected_request"] = None
    
    selected_ids = []
    
    # Left: Request List (table-like)
    with list_col:
        st.subheader("Requests")
        # Header
        col1, col2, col3, col4, col5, col6 = st.columns([0.5, 0.4, 0.4, 0.8, 0.8, 0.5])
        with col1: st.markdown("<h4>Select</h4>", unsafe_allow_html=True)
        with col2: st.markdown("<h4>ID</h4>", unsafe_allow_html=True)
        with col3: st.markdown("<h4>Name</h4>", unsafe_allow_html=True)
        with col4: st.markdown("<h4>Building</h4>", unsafe_allow_html=True)
        with col5: st.markdown("<h4>Apartment</h4>", unsafe_allow_html=True)
        with col6: st.markdown("<h4>Status</h4>", unsafe_allow_html=True)
        st.markdown("---")
        
        for r in filtered:
            col1, col2, col3, col4, col5, col6 = st.columns([0.5, 0.4, 0.4, 0.8, 0.8, 0.5])
            with col1:
                checked = st.checkbox("", value=r['id'] in selected_ids, key=f"chk_{r['id']}")
                if checked:
                    checked_ids.append(r['id'])
                    st.session_state["selected_request"] = r
                else:
                    if st.session_state.get("selected_request") == r:
                        st.session_state["selected_request"] = None
            with col2:
                st.write(r['id'])
            with col3:
                st.write(r['full_name'])
            with col4:
                st.write(r['building'])
            with col5:
                st.write(r['apartment'])
            with col6:
                st.write(r['status'])
    
    st.session_state["selected_ids"] = checked_ids
    
    if not checked_ids:
        st.session_state["selected_request"] = None
    
    if action:
        if not checked_ids:
            st.session_state["error_msg"] = "Error: You have not selected anything. Select an item first before deciding to approve or reject it"
        elif action == 'approve':
            for req_id in checked_ids:
                update_request_status(req_id, 'approved')
            st.session_state["success_msg"] = f"Approved requests: {checked_ids}"
            st.session_state["selected_request"] = None
            st.rerun()
        elif action == 'reject':
            for req_id in checked_ids:
                update_request_status(req_id, 'rejected')
            st.session_state["success_msg"] = f"Rejected requests: {checked_ids}"
            st.session_state["selected_request"] = None
            st.rerun()
    
    # Right: Request Details
    with detail_col:
        req = st.session_state["selected_request"]
        if req:
            st.subheader("Request Details")
            st.markdown(f"### #{req['id']} - {req['title']}")
            st.markdown(f"**Description:** {req['description']}")
            st.markdown(f"**Status:** {req['status']}")
            st.markdown("---")
            st.markdown("**Tenant:**")
            st.markdown(f"{req['full_name']} | {req['phone']}")
            st.markdown(f"Submitted: {req['date']}")
            st.markdown("---")
            st.markdown("**Location:**")
            st.markdown(f"{req['building']} {req['apartment']} {req['location']}")

def update_request_status(request_id, new_status):
    """Update the status of a maintenance request in the database."""
    db_path = Path(__file__).parents[1] / "Data" / "maintenance_app.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE maintenance_requests
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_status, request_id))
    
    conn.commit()
    conn.close()
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
    incoming_requests = get_requests()  # This function should fetch requests from the database
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
def get_requests():
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
