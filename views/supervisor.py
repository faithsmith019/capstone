import streamlit as st
from pathlib import Path
import pickle

def render():
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
        return

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
        st.experimental_rerun()
