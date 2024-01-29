"""Page of the interface for Authentication

"""


import streamlit as st
import ee
import os
import json

class Authentication:
    """Authentication class to connect to Earth Engine 

    Used to get to the account of each user.
    Mandatory to get to any other page of the Interface.

    """

    def __init__(self, session_state):
        self.title = "Authentication"
        self.session_state = session_state

    def show(self):
        current_directory = st.session_state['current_directory']

        image_path = os.path.join(current_directory, 'lib/img/logo.svg')
        st.image(image_path,  use_column_width=True, width=5)
        try:
            st.title(self.title)
            if st.session_state['authenticated']:
                st.success(f'You\'re already authenticated as **{st.session_state["user"]}**', icon="🕶️")
            st.write("Authenticate (or change authenticated user) to Earth Engine with your service account key (a json file)")

            if "mail" not in st.session_state.keys():
                st.session_state['mail'] = "jlimonet@ee-glourb.iam.gserviceaccount.com"
            if "key" not in st.session_state.keys():
                st.session_state['key'] = f"{current_directory}\ee-glourb-7613184e72d6.json"
            if "uploaded_key" not in st.session_state.keys():
                st.session_state['uploaded_key_path'] = ""

            uploaded_key = st.file_uploader("Upload key file", 
                                            type=["json"], 
                                            help = 'Here you can upload your json file !', 
                                            accept_multiple_files=False)

            if st.button("Authenticate"):
                if uploaded_key:
                    self.session_state['uploaded_key_path'] = uploaded_key
                    bytes_data = uploaded_key.getvalue().decode("utf-8")
                    
                    try:
                        credentials = ee.ServiceAccountCredentials(email=json.loads(bytes_data)['client_email'], 
                                                                   key_data=bytes_data)
                        ee.Initialize(credentials)

                        try:
                            ee.data.listAssets({'parent': 'projects/ee-glourb/assets/dgos'})
                        
                            st.session_state['mail'] = json.loads(bytes_data)['client_email']
                            st.session_state['user'] = st.session_state['mail'].split("@")[0]
                            self.session_state['authenticated'] = True

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

        except Exception as e:
            st.error(f"Error: {str(e)}")

    def run(self):
        self.show()

if __name__ == "__main__":        
    session_state = st.session_state
    authentication = Authentication(session_state)
    authentication.run()