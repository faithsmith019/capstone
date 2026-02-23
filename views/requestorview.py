import streamlit as st
from Controller.requestor import mainteanceForm


def render_requestor():
    """Render the requestor home page. All Streamlit calls are contained
    inside this function so importing this module has no side-effects.
    Clicking "Submit a maintenance request" will set `st.session_state['page']`
    to `'maintenanceForm'` so the main app can lazy-load the form.
    """
    session_state = st.session_state
    st.title("Welcome to the Maintenance App!")
    st.write(f"Welcome {session_state.get('name', 'Guest')}!")
    st.write("Please select which action you would like to do:")

    def go_to_maintenance():
        session_state['page'] = 'maintenanceForm'

    if st.button("Submit a maintenance request"):
        go_to_maintenance()

    if st.button("View the status of your existing requests"):
        st.write("This feature is coming soon!")

    if st.button("Edit your profile information"):
        st.write("This feature is coming soon!")

    st.write("Use the navigation buttons on the left to access these features.")