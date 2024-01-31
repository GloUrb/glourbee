"""Home Page of the Interface
"""


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import os
import tempfile
from pathlib import Path
from glourbee import ui

def run_streamlit():
    """Function to make the packaging of the interface work
    """
    os.system('Streamlit run .\src\Homepage.py')

if 'db' not in st.session_state:
    st.session_state['db'] = st.connection('glourbee-db', type='sql', url="sqlite:///ui/lib/db/glourbee-ui.db")
if 'tempdir' not in st.session_state:
    st.session_state['tempdir'] = tempfile.TemporaryDirectory()

class MultiPageApp:
    """Definition of the MultipageApp class that allows to display the entire App as well as the Homepage page.
    Session state variables are initialized if they have no values.
    """
    def __init__(self):
        self.session_state = self.get_session_state()

    @staticmethod
    @st.cache_data(persist=True)
    def get_session_state():
        return {
            "authenticated": False,
            "mail": "jlimonet@ee-glourb.iam.gserviceaccount.com",
            "key": "ee-glourb-58e556f00841.json",
            "uploaded_key_path": "",
            "key_path": ""
    }

    def run(self):
        st.session_state['ui_directory'] = Path(__file__).parent
        ui_directory = st.session_state['ui_directory']

        ui.addHeader()

        st.write("Welcome to the Glourbinterface ! Here we show you how to navigate the app !")

        st.title('Skeleton')
        st.write('The skeleton of the app is built following streamlit\'s integrated [Multipage App](https://docs.streamlit.io/library/advanced-features/multipage-apps) feature. Our entry point is our Homepage.py, and it displays the other pages automatically just by adding a folder pages in our source folder. Useful functions are gathered in the [ee\_interface\_function.py](https://github.com/Julielmnt/Numerical_Project/blob/main/src/ee_interface_function.py) file also in src.' )
        st.image(os.path.join(ui_directory, 'lib/img/skeleton.svg'),  use_column_width=True, width=500)

        st.write('The interface usage is quite linear. Each of the pages won\'t display if the previous pages weren\'t visited and filled since functions implemented in each page need previous pages variables. You can still travel back and forth between the pages, your variables will be saved. ')
        st.title('Authentication page')
        st.write('The Authentication page is to allow you to authenticate to Google Earth Engine (GGE). Most of the function need the connection to GEE to be established in order to work. There are different options to connect : first enter your mail and then load your key, which has a format of a json file. They can or enter the path to that json file or upload it through the file_uploader widget.')
        st.image(os.path.join(ui_directory, 'lib/img/authentication.svg'),  use_column_width=True, width=500)

        st.title('Upload dgos page')
        st.write('The Upload dgos page allows to upload the dgos. First enter the town and river you\'re working on, the map displayed then centers on that said town. Then dgos alrerady uploaded to GEE for this town and river appear (if they exist). We encourage you to not overcrowd the server and therefore to load those dgos or replace them.')
        st.write('You can then or get already uploaded dgos, or upload your own dgos as assets.')
        st.image(os.path.join(ui_directory, 'lib/img/dgo1.svg'),  use_column_width=True, width=500)
        st.subheader('Use an already loaded dgos')   
        st.write('If you choose to use an asset, you\'ll have to enter the number of the one you want from the list above. The dgo loads and is displayed in the map.')
        st.image(os.path.join(ui_directory, 'lib/img/dgo2.svg'),  use_column_width=True, width=500)
        st.subheader('Upload your own dgos')
        st.write('We encourage you to clean the server if you load your own dgos. Wether you do it or not, you will be able to load your dgo with a file uploader widget. Please keep in mind to put in all your files related to your dgos (.shp, .shx...).')
        st.image(os.path.join(ui_directory, 'lib/img/dgo3.svg'),  use_column_width=True, width=500)
        st.write('Your dgos should also be displayed on the map')
        st.image(os.path.join(ui_directory, 'lib/img/dgo4.svg'),  use_column_width=True, width=500)
        
        st.title('Choose metrics page')
        st.write('Here you can first choose the parameters of the images you want to exploit.')
        st.image(os.path.join(ui_directory, 'lib/img/metrics3.svg'),  use_column_width=True, width=500)
        st.image(os.path.join(ui_directory, 'lib/img/metrics1.svg'),  use_column_width=True, width=500)
        st.write('Once you clicked on "run" you\'ll be able to choose what you want to calculate. By default everything is selected. Remove what you want from the list.')
        st.image(os.path.join(ui_directory, 'lib/img/metrics4.svg'),  use_column_width=True, width=500)
        st.image(os.path.join(ui_directory, 'lib/img/metrics2.svg'),  use_column_width=True, width=500)
        st.write('You can then "get you results" and "check the advancement of the tasks".')


if __name__ == "__main__":
    
    session_state = st.session_state 
    if "authenticated" not in st.session_state:
        st.session_state['authenticated'] = False
        st.session_state['dgo_features'] = None
        st.session_state['dgo_assetId'] = None
        st.session_state['run'] = False
        st.session_state['get_results'] = False

    app = MultiPageApp()
    
    app.run()