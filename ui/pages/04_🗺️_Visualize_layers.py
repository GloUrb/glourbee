import streamlit as st

from glourbee import ui

ui.addHeader('Visualize layers on DGOs')

if not st.session_state['authenticated']:
    st.switch_page('pages/01_🕶️_Authentication.py')

st.info('Coming soon', icon='🙃')