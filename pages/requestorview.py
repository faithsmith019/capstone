import streamlit as st


st.title("Welcome Requestor!")
with st.form("maintenance_form", clear_on_submit=True, enter_to_submit=False,border=True,width="stretch",height="content"):
    st.write("In emergencies, please contact a Resident Assistant on call number.")
    st.write("Anything actively leaking, all toilets' broken, A/C or heater not working during extreme temps... please call your RA on call.")
    st.write("If you are unsure if your issue is an emergency please calll the RA number and they can help you determine that.")
    st.write(" UC RA 1(316)295-5232 \n GRH RA 1(316)295-5231")
    st.text_input("Full Name: ")
    st.text_input("Phone Number: ")
    st.date_input("Today's date: ")
    st.text_input("Building: ")
    st.text_input("Apartment Number: ")
    st.text_input("Specific location of issue within apartment (ie bathroom, kitchen, Bedroom A, etc): ")
    st.text_area("Description of repair needed: ")
    st.file_uploader("Upload a photo of the issue (if applicable): ")
    submitted = st.form_submit_button("Submit Request")
    if submitted:
        st.success("Your maintenance request has been submitted successfully!")