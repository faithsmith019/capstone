import streamlit as st
from Controller.requestor import mainteanceForm
import Data.information as data


def show_requestor_notifications():
    user_id = st.session_state.get('username')
    if not user_id:
        return

    notifications = data.get_notifications_for_user(user_id, unread_only=True)
    if notifications:
        st.warning("You have updates on your maintenance requests:")
        for n in notifications:
            st.info(f"{n['created_at']}: {n['message']}")
        data.mark_notifications_read(user_id)


def show_requestor_status():
    user_id = st.session_state.get('username')
    if not user_id:
        st.warning("No requestor logged in.")
        return

    all_requests = data.get_requests(all_status=True)
    
    # Filter requests: match by created_by username (primary match)
    my_requests = [r for r in all_requests if str(r.get('created_by')).strip() == str(user_id).strip()]
    
    if not my_requests:
        st.warning(f"No requests found for user '{user_id}'.")
        st.info("You haven't submitted any maintenance requests yet. Click the 'Submit a Maintenance Request' button to create one.")
        return

    status_filter = st.selectbox("Filter requests by status", ["all", "open", "approved", "queued", "in_progress", "on_hold", "completed", "rejected"], index=0)
    filtered_requests = [r for r in my_requests if status_filter == "all" or r['status'] == status_filter]

    if not filtered_requests:
        st.info(f"No {status_filter} requests found.")
        return

    st.markdown(f"**Showing {len(filtered_requests)} {status_filter if status_filter!='all' else 'all'} request(s)**")
    st.markdown("---")

    for r in filtered_requests:
        st.markdown(f"### Request #{r['id']} - {r['title']}")
        st.markdown(f"**Status:** {r['status']}")
        st.markdown(f"**Submitted:** {r['date']} | Building: {r['building']}, Apt: {r['apartment']}, Location: {r['location']}")
        st.markdown(f"**Description:** {r['description']}")
        st.markdown("---")


def render_requestor():
    """Render the requestor home page. All Streamlit calls are contained
    inside this function so importing this module has no side-effects.
    Clicking a button will set `st.session_state['page']` to the corresponding
    page so the main app can render it.
    """
    session_state = st.session_state
    st.title("🏠 Welcome to the Maintenance App!")
    st.write(f"Welcome {session_state.get('name', 'Guest')}! 👋")

    show_requestor_notifications()

    st.write("Please select which action you would like to do:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Submit a Maintenance Request", use_container_width=True):
            session_state['page'] = 'maintenanceForm'

    with col2:
        if st.button("📋 View Status of Your Requests", use_container_width=True):
            session_state['page'] = 'view_status'

    with col3:
        if st.button("👤 Edit Your Profile Information", use_container_width=True):
            session_state['page'] = 'edit_profile'

    st.write("Use the navigation buttons on the left to access these features.")