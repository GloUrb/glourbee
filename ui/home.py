import streamlit as st

st.header('Welcome', divider=True)

# st.session_state['ui_directory'] = Path(__file__).parent
# ui_directory = st.session_state['ui_directory']

st.markdown("Welcome to the GloUrbEE User Interface! Here's a short description of the GloUrbEE workflow.")

st.image('./ui/lib/img/workflow.png', caption='The GloUrbEE workflow. The red text refers to the UI sections.')