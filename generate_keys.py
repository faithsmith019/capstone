import pickle
from pathlib import Path

import streamlit_authenticator as stauth

#currently isn't updating the hashed passwords file when run, going off of the old johndoe and janesmith passwords, need to figure out how to update the file with the new passwords for requestor, supervisor, and worker
#loveCode
names = ["John Doe", "Jane Smith", "Patrick Star"]
usernames = ["requestor", "supervisor", "worker"]
passwords = ["test1", "test2", "test3"]


hashed_passwords = stauth.Hasher.hash_list(passwords)

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)

