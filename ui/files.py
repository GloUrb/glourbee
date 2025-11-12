import os
import streamlit as st


st.header('Explore and download results', divider=True)
st.info('This module explain how to explore images and masks calculated on GEE and downloaded to this GloUrbEE server.')

st.write('You can access the GloUrbEE files using the WebDAV protocol. Check the instructions for your specific OS below.')
st.title('Windows instructions')

st.title('Ubuntu/Debian instructions')

st.write(f'Open your file explorer, and go to davfs://{os.environ["WEBDAV_URL"]}. The username is {os.environ["WEBDAV_USER"]}, and the password {os.environ["WEBDAV_PASSWORD"]}')
