import requests
import streamlit as st
from pathlib import Path
import pickle
import streamlit_authenticator as stauth
import sqlite3
import os

# Set email credentials
os.environ['EMAIL_SENDER'] = 'falconfacilities2026@gmail.com'
os.environ['EMAIL_PASSWORD'] = 'vefyxrqrpzgmxcrr'

from Data.information import (
    init_db,
    add_user,
    add_maintenance_request,
    get_requests,
    get_request_by_id,
    add_notification,
)
from Controller.emailService import send_status_notification_email


def render_supervisor():
    st.title("👔 Supervisor Dashboard")
    st.write("Manage maintenance requests and user roles.")

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)

    with col1:
        if st.button("📋 View Upcoming Requests", use_container_width=True):
            st.session_state['page'] = 'supervisor_view_upcoming'

    with col2:
        if st.button("📚 View Past Requests", use_container_width=True):
            st.session_state['page'] = 'supervisor_view_past'

    with col3:
        if st.button("✅ View Approved Requests", use_container_width=True):
            st.session_state['page'] = 'supervisor_view_approved'

    with col4:
        if st.button("👤 Add New User", use_container_width=True):
            st.session_state['page'] = 'supervisor_add_user'

    with col5:
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
    st.subheader("📋 Incoming Requests")
    
    # load incoming requests - only open requests
    requests = get_requests(all_status=False)
    
    # Display messages at the top
    if "error_msg" in st.session_state:
        st.error(st.session_state["error_msg"])
        del st.session_state["error_msg"]
    if "success_msg" in st.session_state:
        st.success(st.session_state["success_msg"])
        del st.session_state["success_msg"]
    
    if not requests:
        st.info("No incoming requests at the moment.")
        return
    
    # Retrieve persistent state for selected IDs
    selected_ids = st.session_state.get("supervisor_selected_ids", [])
    
    checked_ids = []
    
    action = None
    
    # Top row: Filter, Select All, Approve, Reject
    top_col1, top_col2, top_col3 = st.columns([0.2, 0.2, 0.6])
    with top_col1:
        status_filter = st.selectbox("Filter Status", ["All","open","approved","queued","in_progress","on_hold","completed","rejected"], key="supervisor_status_filter")
    # with top_col2:
        # select_all = st.checkbox("Select All", key="supervisor_select_all")
    with top_col3:
        button_cols = st.columns(2)
        with button_cols[0]:
            if st.button("✅ Approve Selected", key="supervisor_approve_btn"):
                action = 'approve'
        with button_cols[1]:
            if st.button("❌ Reject Selected", key="supervisor_reject_btn"):
                action = 'reject'
    
    df_to_display = [
        r for r in requests
        if (status_filter=="All" or r["status"]==status_filter)
    ]
    
    #if select_all:
       # checked_ids = [r['id'] for r in df_to_display]
    #else:
    checked_ids = []
    
    # Columns: List + Details (pushed details to the right)
    list_col, detail_col = st.columns([2.5, 1.5])
    
    # Track selected request
    if "supervisor_selected_request" not in st.session_state:
        st.session_state["supervisor_selected_request"] = None
    
    # Left: Request List (table-like)
    with list_col:
        st.markdown("**Requests List**")
        # Header
        col1, col2, col3, col4, col5, col6 = st.columns([0.5, 0.4, 0.4, 0.8, 0.8, 0.5])
        with col1: st.markdown("<h4>Select</h4>", unsafe_allow_html=True)
        with col2: st.markdown("<h4>ID</h4>", unsafe_allow_html=True)
        with col3: st.markdown("<h4>Name</h4>", unsafe_allow_html=True)
        with col4: st.markdown("<h4>Building</h4>", unsafe_allow_html=True)
        with col5: st.markdown("<h4>Apartment</h4>", unsafe_allow_html=True)
        with col6: st.markdown("<h4>Status</h4>", unsafe_allow_html=True)
        st.markdown("---")
        
        if not df_to_display:
            st.info(f"No {status_filter} requests found.")
        else:
            for r in df_to_display:
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 0.4, 0.4, 0.8, 0.8, 0.5])
                with col1:
                    checked = st.checkbox("", value=r['id'] in checked_ids, key=f"supervisor_chk_{r['id']}")
                    if checked and r['id'] not in checked_ids:
                        checked_ids.append(r['id'])
                        st.session_state["supervisor_selected_request"] = r
                    elif not checked and r['id'] in checked_ids:
                        checked_ids.remove(r['id'])
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
    
    # Save state
    st.session_state["supervisor_selected_ids"] = checked_ids
    
    if not checked_ids:
        st.session_state["supervisor_selected_request"] = None
    
    # Handle actions
    if action:
        if not checked_ids:
            st.session_state["error_msg"] = "Error: You have not selected anything. Select an item first before deciding to approve or reject it"
            st.rerun()
        elif action == 'approve':
            for req_id in checked_ids:
                update_request_status(req_id, 'approved')
            st.session_state["success_msg"] = f"Approved {len(checked_ids)} request(s)"
            st.session_state["supervisor_selected_request"] = None
            st.session_state["supervisor_selected_ids"] = []
            st.rerun()
        elif action == 'reject':
            for req_id in checked_ids:
                update_request_status(req_id, 'rejected')
            st.session_state["success_msg"] = f"Rejected {len(checked_ids)} request(s)"
            st.session_state["supervisor_selected_request"] = None
            st.session_state["supervisor_selected_ids"] = []
            st.rerun()
    
    # Right: Request Details
    with detail_col:
        req = st.session_state.get("supervisor_selected_request")
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

    # Add a notification for the requestor and fire an email if available
    req = get_request_by_id(request_id)
    if req is not None:
        requestor_id = req.get('created_by') or req.get('requestor_email') or ''
        msg = f"Your maintenance request #{request_id} status has been changed to '{new_status}'."
        add_notification(requestor_id, request_id, msg, notification_type="status_change")

        requestor_email = req.get('requestor_email')
        if requestor_email:
            success, info = send_status_notification_email(requestor_email, request_id, new_status, msg, req.get('full_name') or "")
            if not success:
                st.warning(f"Email notification failed for request #{request_id}: {info}")
    else:
        st.warning(f"Request #{request_id} not found while creating notification")

    return True
def showIncomingRequests():
    st.subheader("Incoming Requests")
    st.write("This section will display all incoming maintenance requests for the supervisor to review and assign to workers.")
    incoming_requests = get_requests(all_status=False)  # open requests only
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


def showApprovedRequests():
    st.subheader("Approved Requests")
    approved_requests = [r for r in get_requests(all_status=True) if r['status'] == 'approved']
    if not approved_requests:
        st.info("No approved requests at this time.")
        return

    for req in approved_requests:
        st.write(f"**Request ID:** {req['id']}")
        st.write(f"**Title:** {req['title']}")
        st.write(f"**Description:** {req['description']}")
        st.write(f"**Status:** {req['status']}")
        st.write(f"**Created By:** {req['created_by']}")
        st.write(f"**Assigned To:** {req['assigned_to']}")
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
def showPastRequests():
    st.subheader("Past Requests")
    all_requests = get_requests(all_status=True)
    past_requests = [r for r in all_requests if r['status'] == 'completed']

    if not past_requests:
        st.info("No past requests found.")
        return []

    for req in past_requests:
        st.write(f"**Request ID:** {req['id']}")
        st.write(f"**Title:** {req['title']}")
        st.write(f"**Description:** {req['description']}")
        st.write(f"**Status:** {req['status']}")
        st.write(f"**Created By:** {req['created_by']}")
        st.write(f"**Assigned To:** {req['assigned_to']}")
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

    return past_requests
