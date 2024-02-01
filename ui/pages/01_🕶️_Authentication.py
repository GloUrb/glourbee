"""Page of the interface for Authentication

"""

import streamlit as st
import ee
import json

from glourbee import ui

ui.addHeader('Authenticate')

if st.session_state['authenticated']:
    st.success(f'You\'re already authenticated as **{st.session_state["user"]}**', icon="🕶️")
st.write("Authenticate (or change authenticated user) to Earth Engine with your service account key (a json file)")

uploaded_key = st.file_uploader("Upload key file", 
                                type=["json"], 
                                help = 'Here you can upload your json file !', 
                                accept_multiple_files=False)

if st.button("Authenticate with JSON key"):
    if uploaded_key:
        st.session_state['uploaded_key_path'] = uploaded_key
        bytes_data = uploaded_key.getvalue().decode("utf-8")
        
        try:
            credentials = ee.ServiceAccountCredentials(email=json.loads(bytes_data)['client_email'], 
                                                        key_data=bytes_data)
            ee.Initialize(credentials)

            try:
                ee.data.listAssets({'parent': 'projects/ee-glourb/assets/dgos'})
            
                st.session_state['mail'] = json.loads(bytes_data)['client_email']
                st.session_state['user'] = st.session_state['mail'].split("@")[0]
                st.session_state['authenticated'] = True

                st.balloons()
                st.success(f"Authenticated as **{st.session_state['user']}**", icon="🕶️")

            except ee.EEException as e:
                st.error("Your account have no access to the ee-glourb Earth Engine project", icon="🚨")

        except ee.EEException as e:
            st.error("Authentication failed", icon="🚨")

    else:
        st.write("Please upload your JSON key file")
else:
    st.write("Please enter your credentials.")
