# -*- coding: utf-8 -*-

"""Home Page of the Interface
"""

import streamlit as st
import json
import ee

from alembic.config import Config
from alembic import command
from glourbee import __version__ as glourbee_version

st.set_page_config(layout="wide")


@st.cache_resource
def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

run_migrations()


with st.sidebar:
    if "user" in st.session_state.keys() and st.session_state["user"]["is_logged_in"]:
        st.success(f'Authenticated as **{st.session_state["user"]["name"]}**', icon="😎")
        if st.button('Logout'):
            st.session_state['user']['name'] = None
            st.session_state['user']['is_logged_in'] = False
            st.rerun()

    else:
        st.warning(f'**Unauthenticated**', icon="🥸")

    st.write(f'GloUrbEE version: ```{glourbee_version}```')
    st.write('[Report a bug or ask for new feature](https://github.com/EVS-GIS/glourbee/issues)')

st.image('/app/ui/lib/img/logo.svg')

if not "user" in st.session_state.keys() or not st.session_state["user"]["is_logged_in"]:
    st.warning("Please login first")
    uploaded_key = st.file_uploader("Upload key file", 
                                    type=["json"], 
                                    help = 'Here you can upload your json key file !', 
                                    accept_multiple_files=False)

    if uploaded_key:
        key_json = json.load(uploaded_key)

        st.session_state['user'] = {
            'is_logged_in': False,
            'name': None
        }
        
        try:
            credentials = ee.ServiceAccountCredentials(email=key_json['client_email'], 
                                                        key_data=json.dumps(key_json))
            with st.spinner("Logging in..."):
                ee.Initialize(credentials)

            try:
                ee.data.listAssets({'parent': 'projects/ee-glourb/assets'})
            
                st.session_state['user']['name'] = key_json['client_email'].split("@")[0]
                st.session_state['user']['is_logged_in'] = True

                st.rerun()

            except ee.EEException as e:
                st.error(f"Your account have no access to the ee-glourb Earth Engine project: {e}", icon="🚨")

        except ee.EEException as e:
            st.error("Authentication failed", icon="🚨")

    st.stop()

pg = st.navigation([
        st.Page("home.py", title="Home page", icon="🏠"),
        st.Page("extraction.py", title="Extraction zones", icon="🌍"), 
        st.Page('gee.py', title="GEE processing", icon="☁️"),
        st.Page("metrics.py", title="Metrics calculation", icon="📈"),
        st.Page("tasks.py", title="Tasks manager", icon="📋")
    ])
pg.run()