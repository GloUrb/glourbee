"""Home Page of the Interface
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import os
import tempfile
from pathlib import Path
from glourbee import ui

if 'tempdir' not in st.session_state:
    st.session_state['tempdir'] = tempfile.TemporaryDirectory()
if "authenticated" not in st.session_state:
    st.session_state['authenticated'] = False
if 'extraction_zones' not in st.session_state:
    st.session_state['extraction_zones'] = {'tableId': None, 'assetId': None, 'features': None}


st.session_state['ui_directory'] = Path(__file__).parent
ui_directory = st.session_state['ui_directory']

ui.addHeader('Welcome')
st.warning('The GloUrbEE-UI is actually a beta feature. Please report any bug, enhancement or feature request to [the project\'s GitHub](https://github.com/EVS-GIS/glourbee/issues).', icon='⚠️')

st.write("Welcome to the GloUrbEE User Interface ! Here's how to use the app")

st.write('The interface usage is quite linear. Each pages won\'t display if the previous pages weren\'t visited and filled since functions implemented in each page need previous pages variables. You can still travel back and forth between the pages, your variables will be saved. ')
st.info('Detailed tutorial coming soon', icon='🙃')

st.title('Authentication page')
st.write('The Authentication page allow you to authenticate to Google Earth Engine (GEE). Most of the function need the connection to GEE to be established in order to work. For the moment, only service account JSON key is supported.')
#st.image(os.path.join(ui_directory, 'lib/img/authentication.svg'),  use_column_width=True, width=500)

st.title('Manage extraction zones page')
st.write('The *Manage extraction zones* page allows to select extraction zones, upload new ones or delete extraction zones previously uploaded on GEE.')
#st.image(os.path.join(ui_directory, 'lib/img/zone1.svg'),  use_column_width=True, width=500)
#st.subheader('Use an already loaded zones')   
#st.write('If you choose to use an asset, you\'ll have to enter the number of the one you want from the list above. The zone loads and is displayed in the map.')
#st.image(os.path.join(ui_directory, 'lib/img/zone2.svg'),  use_column_width=True, width=500)
#st.subheader('Upload your own zones')

# st.write('We encourage you to clean the server if you load your own zones. Wether you do it or not, you will be able to load your zone with a file uploader widget. Please keep in mind to put in all your files related to your zones (.shp, .shx...).')
# st.image(os.path.join(ui_directory, 'lib/img/zone3.svg'),  use_column_width=True, width=500)
# st.write('Your zones should also be displayed on the map')
# st.image(os.path.join(ui_directory, 'lib/img/zone4.svg'),  use_column_width=True, width=500)

st.title('Manage metrics page')
st.write('Select a metrics dataset, download it locally, or start a new metrics dataset calculation.')
# st.image(os.path.join(ui_directory, 'lib/img/metrics3.svg'),  use_column_width=True, width=500)
# st.image(os.path.join(ui_directory, 'lib/img/metrics1.svg'),  use_column_width=True, width=500)
# st.write('Once you clicked on "run" you\'ll be able to choose what you want to calculate. By default everything is selected. Remove what you want from the list.')
# st.image(os.path.join(ui_directory, 'lib/img/metrics4.svg'),  use_column_width=True, width=500)
# st.image(os.path.join(ui_directory, 'lib/img/metrics2.svg'),  use_column_width=True, width=500)
# st.write('You can then "get you results" and "check the advancement of the tasks".')

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