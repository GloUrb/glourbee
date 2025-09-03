import streamlit as st

st.header('Welcome', divider=True)

# st.session_state['ui_directory'] = Path(__file__).parent
# ui_directory = st.session_state['ui_directory']

st.markdown("Welcome to the GloUrbEE User Interface! Here's how to use the app.")

st.write('The interface usage is quite linear. Each pages won\'t display if the previous pages weren\'t visited and filled since functions implemented in each page need previous pages variables. You can still travel back and forth between the pages, your variables will be saved. ')

st.title('Manage extraction zones page')
st.write('The *Manage extraction zones* page allows to select extraction zones, upload new ones or delete extraction zones previously uploaded on GEE.')

st.title('Manage metrics page')
st.write('Select a metrics dataset, download it locally, or start a new metrics dataset calculation.')

st.title('Visualize layers page')
st.info('Coming soon', icon='🙃')
st.markdown('''
This page will allow you to visualize the metrics calculated and the corresponding layers for a few set of extraction zones:
- WATER CHANNEL
- ACTIVE CHANNEL
- VEGETATION
- NDVI
- MNDWI
''')

st.title('Tasks manager page')
st.markdown('''
Monitor the tasks you sent to GEE. Refreshing this page will also update the tasks state in the GloUrbEE-UI database.
''')
