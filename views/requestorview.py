import streamlit as st
from Controller.requestor import mainteanceForm


def render_requestor():
    """Render the requestor home page. All Streamlit calls are contained
    inside this function so importing this module has no side-effects.
    Clicking a button will set `st.session_state['page']` to the corresponding
    page so the main app can render it.
    """
    session_state = st.session_state
    st.title("🏠 Welcome to the Maintenance App!")
    st.write(f"Welcome {session_state.get('name', 'Guest')}! 👋")
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