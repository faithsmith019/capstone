import streamlit as st
from pathlib import Path
import pickle
import streamlit_authenticator as stauth

def render_supervisor():
    st.title("Supervisor View — User Role Management")

    CREDENTIALS_FILE = Path(__file__).parents[1] / 'hashed_pw.pkl'

    def load_credentials():
        if CREDENTIALS_FILE.exists():
            with CREDENTIALS_FILE.open('rb') as f:
                return pickle.load(f)
        return {'usernames': {}}

    def save_credentials(creds):
        with CREDENTIALS_FILE.open('wb') as f:
            pickle.dump(creds, f)

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
        st.success('Roles updated')
        st.rerun()

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
                st.success(f'User {new_username} created with role {new_role}')
                st.rerun()
