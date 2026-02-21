import pickle
from pathlib import Path

import streamlit_authenticator as stauth

# Initial default user credentials for the application
# To add/modify users here, edit the lists below and run this script
# Additional users can be registered via the app's Register tab
names = ["Requestor User", "Supervisor User", "Worker User"]
usernames = ["requestor", "supervisor", "worker"]
passwords = ["XXXX", "XXXX", "XXXX"] # Plaintext passwords for initial users (will be hashed)

# Hash passwords and create credentials dict
hashed_passwords = stauth.Hasher.hash_list(passwords)

credentials = {"usernames": {}}
def infer_role_from_username(uname: str) -> str:
    u = uname.lower()
    if 'requestor' in u:
        return 'requestor'
    if 'supervisor' in u or 'admin' in u:
        return 'supervisor'
    if 'worker' in u or 'staff' in u:
        return 'worker'
    return 'requestor'

for uname, nm, pw in zip(usernames, names, hashed_passwords):
    role = infer_role_from_username(uname)
    credentials["usernames"][uname] = {"name": nm, "password": pw, "role": role}

# Save credentials to pickle file
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(credentials, file)

print("Updated hashed_pw.pkl with default users:")
for uname, nm in zip(usernames, names):
    print(f"  - {uname}: {nm} (role: {credentials['usernames'][uname].get('role')})")

