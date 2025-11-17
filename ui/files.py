import os
import streamlit as st

st.header('Explore and download results', divider=True)

st.link_button("Access the GloUrbEE File Explorer", os.environ["FILES_URL"])
st.write(f'''
         Login with the following credentials:
         - Username: `{os.environ["FILES_USER"]}`
         - Password: `{os.environ["FILES_PASSWORD"]}`
         ''')

st.write(f"You can also access the GloUrbeEE File Server from FileZilla with the SFTP protocol, using the same user and password with the host `{os.environ["SFTP_HOST"]}` and port `{os.environ["SFTP_PORT"]}`.")
