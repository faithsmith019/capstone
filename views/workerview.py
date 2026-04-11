import streamlit as st
import Data.information as data


def render_worker():
    st.title("👔 Worker Dashboard")
    st.write("Manage work requests")

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


def betterDisplayIncomingWorkRequests():
    """Display incoming work requests (unassigned only, sorted by seen status)."""
    all_requests = data.get_requests(all_status=True)
    
    # Filter: open requests that are UNASSIGNED (not yet assigned to anyone)
    # Note: assigned_to is empty string when unassigned
    incoming = [
        r for r in all_requests 
        if r['status'] == 'open' and not r.get('assigned_to')
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
    with top_col2:
        select_all = st.checkbox("Select All", key="select_all_worker")
    with top_col3:
        if st.button("🤝 Assign Selected to Me"):
            action = 'assign_to_me'
    
    # Apply additional filter if checked
    if show_filter:
        filtered = [r for r in incoming if not r.get('worker_viewed')]
    else:
        filtered = incoming
    
    if select_all:
        checked_ids = [r['id'] for r in filtered]
    
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



def showIncomingWorkRequests():
    """Displays incoming work requests using the better table layout."""
    betterDisplayIncomingWorkRequests()


def showPastWorkRequests():
    """Display completed/closed work requests."""
    st.subheader("Past Work Requests")
    all_requests = data.get_requests(all_status=True)
    past = [r for r in all_requests if r['status'] in ('closed', 'completed')]
    
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


def showAssignedWorkRequests():
    """Display assigned work requests with filtering."""
    st.subheader("Assigned Work Requests")
    user = st.session_state.get('username')
    if not user:
        st.warning("Please log in as a worker to see assigned work requests.")
        return

    all_requests = data.get_requests(all_status=True)
    
    # Filter to assigned requests (not completed/closed)
    # Note: assigned_to is empty string when unassigned
    assigned_requests = [
        r for r in all_requests 
        if r.get('assigned_to') and r['status'] not in ('closed', 'completed')
    ]
    
    if not assigned_requests:
        st.info("No assigned work requests at this time.")
        return
    
    # Get unique assigned_to values for filter
    assigned_to_values = sorted(set(r.get('assigned_to') for r in assigned_requests if r.get('assigned_to')))
    
    # Filter by assigned_to
    selected_worker = st.selectbox(
        "Filter by assigned worker",
        ["All"] + assigned_to_values,
        key="worker_filter"
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
    
    # Display
    for req in sorted_requests:
        is_mine = "👤 MY REQUEST" if req.get('assigned_to') == user else f"👥 Assigned to {req.get('assigned_to')}"
        st.write(f"**[{is_mine}] Request ID:** {req['id']}")
        st.write(f"**Title:** {req['title']}")
        st.write(f"**Description:** {req['description']}")
        st.write(f"**Status:** {req['status']}")
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



