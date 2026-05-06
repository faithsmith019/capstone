import streamlit as st
import Data.information as data
import os
from Controller.emailService import send_status_notification_email

# Set email credentials
os.environ['EMAIL_SENDER'] = 'falconfacilities2026@gmail.com'
os.environ['EMAIL_PASSWORD'] = 'vefyxrqrpzgmxcrr'

# Display unread notifications for the logged-in worker
# Inputs: none directly, reads current user from st.session_state['username']
# Output: displays notification warnings/info in Streamlit and marks notifications as read
# Side effects: updates notification read state for the current user
def show_worker_notifications():
    """Display unread notifications for the worker."""
    user_id = st.session_state.get('username')
    if not user_id:
        return

    notifications = data.get_notifications_for_user(user_id, unread_only=True)
    if notifications:
        st.warning("You have updates on your maintenance requests:")
        for n in notifications:
            st.info(f"{n['created_at']}: {n['message']}")
        data.mark_notifications_read(user_id)

# Render the worker dashboard page
# Inputs: none directly, uses st.session_state for current user and page state
# Output: displays dashboard buttons and triggers page navigation via st.session_state
def render_worker():
    st.title("👔 Worker Dashboard")
    st.write("Manage work requests")

    show_worker_notifications()

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        if st.button("📋 View Incoming Requests", use_container_width=True):
            st.session_state['page'] = 'worker_view_upcoming'

    with col2:
        if st.button("📚 View Past Requests", use_container_width=True):
            st.session_state['page'] = 'worker_view_past'

    with col3:
        if st.button("View Assigned Requests", use_container_width=True):
            st.session_state['page'] = 'worker_view_assigned'

# Display incoming work requests in a table layout
# Inputs: none directly, reads requests from Data.information.get_requests and streamlit state
# Output: renders a selectable list of incoming requests and a detail panel; supports assign-to-me action
def betterDisplayIncomingWorkRequests():
    """Display incoming work requests (approved and queued unassigned, sorted by seen status)."""
    all_requests = data.get_requests(all_status=True)
    
    # Filter: approved or queued requests that are UNASSIGNED (not yet assigned to anyone)
    # Approved = reviewed but not seen by worker yet
    # Queued = seen by worker, waiting for assignment
    # Note: assigned_to is empty string when unassigned
    incoming = [
        r for r in all_requests 
        if r['status'] in ('approved', 'queued') and not r.get('assigned_to')
    ]
    
    # Sort: unseen first, then seen
    incoming.sort(key=lambda x: (bool(x.get('worker_viewed')), x['id']))
    
    # Display messages at the top
    if "error_msg" in st.session_state:
        st.error(st.session_state["error_msg"])
        del st.session_state["error_msg"]
    if "success_msg" in st.session_state:
        st.success(st.session_state["success_msg"])
        del st.session_state["success_msg"]
    
    if not incoming:
        st.info("No incoming work requests at the moment.")
        return
    
    checked_ids = []
    action = None
    
    # Top row: Filter, Select All, Assign to Me
    top_col1, top_col2, top_col3 = st.columns([0.3, 0.2, 0.5])
    with top_col1:
        show_filter = st.checkbox("Show only unseen", value=True, key="filter_unseen")
    #with top_col2:
        #select_all = st.checkbox("Select All", key="select_all_worker")
    with top_col3:
        if st.button("🤝 Assign Selected to Me"):
            action = 'assign_to_me'
    
    # Apply additional filter if checked
    if show_filter:
        filtered = [r for r in incoming if not r.get('worker_viewed')]
    else:
        filtered = incoming
    
    #if select_all:
        #checked_ids = [r['id'] for r in filtered]
    
    checked_ids = []
    
    # Columns: List + Details
    list_col, detail_col = st.columns([2.5, 1.5])
    
    # Track selected request
    if "selected_work_request" not in st.session_state:
        st.session_state["selected_work_request"] = None
    
    selected_ids = []
    
    # Left: Request List (table-like)
    with list_col:
        st.subheader("Incoming Requests")
        # Header
        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 0.3, 0.4, 0.4, 0.8, 0.8, 0.5])
        with col1: st.markdown("<h4>Select</h4>", unsafe_allow_html=True)
        with col2: st.markdown("<h4>Seen</h4>", unsafe_allow_html=True)
        with col3: st.markdown("<h4>ID</h4>", unsafe_allow_html=True)
        with col4: st.markdown("<h4>Name</h4>", unsafe_allow_html=True)
        with col5: st.markdown("<h4>Building</h4>", unsafe_allow_html=True)
        with col6: st.markdown("<h4>Apartment</h4>", unsafe_allow_html=True)
        with col7: st.markdown("<h4>Status</h4>", unsafe_allow_html=True)
        st.markdown("---")
        
        for r in filtered:
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 0.3, 0.4, 0.4, 0.8, 0.8, 0.5])
            with col1:
                checked = st.checkbox("", value=r['id'] in selected_ids, key=f"worker_chk_{r['id']}")
                if checked:
                    checked_ids.append(r['id'])
                    st.session_state["selected_work_request"] = r
                    # Mark as seen when selected
                    data.mark_request_seen(r['id'])
                else:
                    if st.session_state.get("selected_work_request") == r:
                        st.session_state["selected_work_request"] = None
            with col2:
                seen_status = "✓" if r.get('worker_viewed') else "○"
                st.write(seen_status)
            with col3:
                st.write(r['id'])
            with col4:
                st.write(r['full_name'])
            with col5:
                st.write(r['building'])
            with col6:
                st.write(r['apartment'])
            with col7:
                st.write(r['status'])
    
    st.session_state["selected_ids_worker"] = checked_ids
    
    if not checked_ids:
        st.session_state["selected_work_request"] = None
    
    if action:
        if not checked_ids:
            st.session_state["error_msg"] = "Error: You have not selected anything. Select an item first before assigning to yourself."
        elif action == 'assign_to_me':
            worker_id = st.session_state.get('username')
            for req_id in checked_ids:
                data.assign_request_to_worker(req_id, worker_id)
            st.session_state["success_msg"] = f"Assigned {len(checked_ids)} request(s) to yourself"
            st.session_state["selected_work_request"] = None
            st.rerun()
    
    # Right: Request Details
    with detail_col:
        req = st.session_state["selected_work_request"]
        if req:
            st.subheader("Request Details")
            st.markdown(f"### #{req['id']} - {req['title']}")
            st.markdown(f"**Description:** {req['description']}")
            st.markdown(f"**Status:** {req['status']}")
            st.markdown(f"**Seen:** {'Yes ✓' if req.get('worker_viewed') else 'No ○'}")
            assigned_to = req.get('assigned_to', '')
            assigned_display = 'Unassigned' if not assigned_to else assigned_to
            st.markdown(f"**Assigned to:** {assigned_display}")
            st.markdown("---")
            st.markdown("**Tenant:**")
            st.markdown(f"{req['full_name']} | {req['phone']}")
            st.markdown(f"Submitted: {req['date']}")
            st.markdown("---")
            st.markdown("**Location:**")
            st.markdown(f"{req['building']} {req['apartment']} {req['location']}")



# Wrapper to display incoming work requests
# Inputs: none directly
# Output: delegates to betterDisplayIncomingWorkRequests to render the requests UI
def showIncomingWorkRequests():
    """Displays incoming work requests using the better table layout."""
    betterDisplayIncomingWorkRequests()

# Display completed work requests in a readable list
# Inputs: none directly, reads all requests from Data.information.get_requests
# Output: renders completed request details in the Streamlit UI
def showPastWorkRequests():
    """Display completed work requests."""
    st.subheader("Past Work Requests")
    all_requests = data.get_requests(all_status=True)
    past = [r for r in all_requests if r['status'] == 'completed']
    
    if not past:
        st.info("No past work requests to show.")
        return

    # Simple list display (not table)
    for req in past:
        st.write(f"**Request ID:** {req['id']}")
        st.write(f"**Title:** {req['title']}")
        st.write(f"**Description:** {req['description']}")
        st.write(f"**Status:** {req['status']}")
        st.write(f"**Assigned To:** {req.get('assigned_to', 'Unassigned')}")
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


# Wrapper to display assigned work requests for the worker
# Inputs: none directly
# Output: delegates to betterDisplayAssignedWorkRequests to render the assigned request UI
def showAssignedWorkRequests():
    """Displays assigned work requests with editing capability."""
    betterDisplayAssignedWorkRequests()

# Display assigned work requests and allow the worker to update status, priority, notes, or hold reason
# Inputs: none directly, reads current user and requests from state/data functions
# Output: renders the assigned requests list and an edit form for the selected request
def betterDisplayAssignedWorkRequests():
    """Display assigned work requests with editing functionality."""
    user = st.session_state.get('username')
    if not user:
        st.warning("Please log in as a worker to see assigned work requests.")
        return

    all_requests = data.get_requests(all_status=True)
    
    # Filter to assigned requests (not completed or on_hold)
    assigned_requests = [
        r for r in all_requests 
        if r.get('assigned_to') and r['status'] not in ('completed', 'on_hold')
    ]
    
    # Display messages at the top
    if "error_msg" in st.session_state:
        st.error(st.session_state["error_msg"])
        del st.session_state["error_msg"]
    if "success_msg" in st.session_state:
        st.success(st.session_state["success_msg"])
        del st.session_state["success_msg"]
    
    if not assigned_requests:
        st.info("No assigned work requests at this time.")
        return
    
    # Get unique assigned_to values for filter
    assigned_to_values = sorted(set(r.get('assigned_to') for r in assigned_requests if r.get('assigned_to')))
    
    # Filter by assigned_to
    selected_worker = st.selectbox(
        "Filter by assigned worker",
        ["All"] + assigned_to_values,
        key="worker_filter_assigned"
    )
    
    if selected_worker == "All":
        filtered = assigned_requests
    else:
        filtered = [r for r in assigned_requests if r.get('assigned_to') == selected_worker]
    
    if not filtered:
        st.info("No requests assigned to selected worker.")
        return
    
    # Sort: current user's requests first, then others
    my_requests = [r for r in filtered if r.get('assigned_to') == user]
    other_requests = [r for r in filtered if r.get('assigned_to') != user]
    sorted_requests = my_requests + other_requests
    
    # Columns: List + Details/Edit
    list_col, detail_col = st.columns([2.5, 1.5])
    
    # Track selected request
    if "selected_assigned_request" not in st.session_state:
        st.session_state["selected_assigned_request"] = None
    
    # Left: Request List (table-like)
    with list_col:
        st.subheader("Assigned Requests")
        # Header
        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 0.4, 0.4, 0.4, 0.8, 0.8, 0.5])
        with col1: st.markdown("<h4>Select</h4>", unsafe_allow_html=True)
        with col2: st.markdown("<h4>ID</h4>", unsafe_allow_html=True)
        with col3: st.markdown("<h4>Name</h4>", unsafe_allow_html=True)
        with col4: st.markdown("<h4>Priority</h4>", unsafe_allow_html=True)
        with col5: st.markdown("<h4>Building</h4>", unsafe_allow_html=True)
        with col6: st.markdown("<h4>Apartment</h4>", unsafe_allow_html=True)
        with col7: st.markdown("<h4>Status</h4>", unsafe_allow_html=True)
        st.markdown("---")
        
        for r in sorted_requests:
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 0.4, 0.4, 0.4, 0.8, 0.8, 0.5])
            with col1:
                checked = st.checkbox("", value=st.session_state.get("selected_assigned_request") == r, key=f"assigned_chk_{r['id']}")
                if checked:
                    st.session_state["selected_assigned_request"] = r
                elif st.session_state.get("selected_assigned_request") == r:
                    st.session_state["selected_assigned_request"] = None
            with col2:
                st.write(r['id'])
            with col3:
                st.write(r['full_name'])
            with col4:
                priority = r.get('priority', 'normal') or 'normal'
                st.write(priority.title())
            with col5:
                st.write(r['building'])
            with col6:
                st.write(r['apartment'])
            with col7:
                st.write(r['status'])
    
    # Right: Request Details and Edit Form
    with detail_col:
        req = st.session_state["selected_assigned_request"]
        if req:
            st.subheader("Edit Request")
            st.markdown(f"### #{req['id']} - {req['title']}")
            st.markdown(f"**Description:** {req['description']}")
            
            # Edit form
            with st.form(key=f"edit_form_{req['id']}"):
                # Status dropdown
                status_options = ['in_progress', 'on_hold', 'completed']
                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_options.index(req['status']) if req['status'] in status_options else 0
                )
                
                # Priority dropdown
                priority_options = ['low', 'normal', 'high', 'urgent']
                current_priority = req.get('priority', 'normal') or 'normal'
                new_priority = st.selectbox(
                    "Priority",
                    priority_options,
                    index=priority_options.index(current_priority) if current_priority in priority_options else 1
                )
                
                # Hold Reason (only if status is on_hold)
                new_hold_reason = None
                if new_status == 'on_hold':
                    new_hold_reason = st.text_area(
                        "Hold Reason",
                        value=req.get('hold_reason', ''),
                        height=100
                    )
                
                # Notes
                new_notes = st.text_area(
                    "Notes",
                    value=req.get('notes', ''),
                    height=150
                )
                
                submitted = st.form_submit_button("Update Request")
                
                if submitted:
                    # Update the request
                    data.update_request_details(
                        req['id'],
                        status=new_status,
                        priority=new_priority,
                        hold_reason=new_hold_reason,
                        notes=new_notes
                    )
                    
                    # If status changed to completed, send notification
                    if new_status == 'completed' and req['status'] != 'completed':
                        # Send notification and email
                        requestor_id = req.get('created_by') or req.get('requestor_email') or ''
                        msg = f"Your maintenance request #{req['id']} has been completed."
                        data.add_notification(requestor_id, req['id'], msg, notification_type="status_change")
                        
                        requestor_email = req.get('requestor_email')
                        if requestor_email:
                            success, info = send_status_notification_email(requestor_email, req['id'], 'completed', msg, req.get('full_name') or "")
                            if not success:
                                st.warning(f"Email notification failed: {info}")
                    
                    st.session_state["success_msg"] = "Request updated successfully!"
                    st.session_state["selected_assigned_request"] = None
                    st.rerun()
            
            # Display current details
            st.markdown("---")
            st.markdown("**Current Details:**")
            st.markdown(f"**Status:** {req['status']}")
            st.markdown(f"**Priority:** {(req.get('priority') or 'normal').title()}")
            if req.get('hold_reason'):
                st.markdown(f"**Hold Reason:** {req['hold_reason']}")
            if req.get('notes'):
                st.markdown(f"**Notes:** {req['notes']}")
            st.markdown("---")
            st.markdown("**Tenant:**")
            st.markdown(f"{req['full_name']} | {req['phone']}")
            st.markdown(f"Submitted: {req['date']}")
            st.markdown("---")
            st.markdown("**Location:**")
            st.markdown(f"{req['building']} {req['apartment']} {req['location']}")
        else:
            st.info("Select a request to edit its details.")



