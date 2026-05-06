import streamlit as st
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
from Data.information import add_maintenance_request


def mainteanceForm():
    """Render the requestor maintenance request submission form.

    Inputs: form fields entered by the current logged-in requestor.
    Output: creates a maintenance request record when the form is submitted.
    """
    st.title("Welcome Requestor!")
    with st.form("maintenance_form", clear_on_submit=True, enter_to_submit=False, border=True, width="stretch", height="content"):
            st.write("In emergencies, please contact a Resident Assistant on call number.")
            st.write("Anything actively leaking, all toilets' broken, A/C or heater not working during extreme temps... please call your RA on call number.")
            st.write("If you are unsure if your issue is an emergency please calll the RA number and they can help you determine that.")
            st.write(" UC RA 1(316)295-5232 \n GRH RA 1(316)295-5231")
            st.text_input("Full Name:", key="full_name")
            st.text_input("Email Address (for notifications):", key="requestor_email")
            st.text_input("Phone Number:", key="phone")
            st.date_input("Today's date:", key="date")
            st.text_input("Building:", key="building")
            st.text_input("Apartment Number:", key="apartment")
            st.text_input("Specific location of issue within apartment (ie bathroom, kitchen, Bedroom A, etc):", key="location")
            st.text_area("Description of repair needed:", key="description")
            st.file_uploader("Upload a photo of the issue (if applicable):", key="photo")
            submitted = st.form_submit_button("Submit Request")
            if submitted:
                st.success("Your maintenance request has been submitted successfully!")
                # Persist the requestor's maintenance request to the database.
                add_maintenance_request(
                    title="Maintenance Request",
                    description=st.session_state.get("description", ""),
                    created_by=st.session_state.get("username", "requestor"),
                    requestor_email=st.session_state.get("requestor_email", ""),
                    assigned_to="",
                    status="open",
                    created_at=str(st.session_state.get("date", "")),
                    updated_at=str(st.session_state.get("date", "")),
                    full_name=st.session_state.get("full_name", ""),
                    phone=st.session_state.get("phone", ""),
                    date=str(st.session_state.get("date", "")),
                    building=st.session_state.get("building", ""),
                    apartment=st.session_state.get("apartment", ""),
                    location=st.session_state.get("location", "")
                )
