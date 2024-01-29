""" Page for choosing the metrics in the interface
"""
import streamlit as st
import streamlit as st
import ee_interface_function as eef
import ee
import tempfile
import os


class PageTwo:
    """PageTwo class for choosing and downlloading the metrics

    Let the user choose it's metrics and builds the csv file for downloading.

    """
    def __init__(self, session_state):
        self.title = "Choosing metrics"
        self.ee_project_name = "ee-glourb"
        self.session_state = session_state
        self.start = '1980-01-01'
        self.end = '2030-12-31'
        self.dgo_asset = self.session_state['dgo_assetId']
        self.cloud_filter = 80
        self.cloud_masking = True
        self.mosaic_same_day = True
        self.split_size = 25
        self.run = st.session_state['run']
        self.get_results = st.session_state['get_results']
        self.task = None
        st.session_state['tempdir'] = tempfile.mkdtemp(prefix='glourbee_')

    def glourbmetrics_params(self):
        glourbmetrics_params = {
        'ee_project_name': self.ee_project_name,
        'dgo_asset': self.dgo_asset,
        'start': self.start,
        'end': self.end,
        'cloud_filter': self.cloud_filter,
        'cloud_masking': True,
        'mosaic_same_day': True,
        'split_size': 25,
    }
        return glourbmetrics_params

    def show(self):
        current_directory = os.getcwd()
        image_path = f'{current_directory}\logo.svg'
        st.image(image_path,  use_column_width=True, width=5)

        st.title(self.title)
        col1, col2 = st.columns(2)
        start = col1.date_input('start')
        self.start = start.strftime('%Y-%m-%d')
        stop = col2.date_input('stop')
        self.stop = stop.strftime('%Y-%m-%d')
        self.cloud_filter= st.slider('cloud filter', min_value= 0, max_value= 100, value = 80)
        self.cloud_masking = st.toggle('cloud masking', value = True)
        self.mosaic_same_day = st.toggle('mosaic same day', value = True)

        glourbmetrics_params = self.glourbmetrics_params()
        self.run = st.button('Run', help = 'To start the workflow once you\'ve chosen your parameters')

        if self.run or st.session_state['run']: 
            from glourbee import workflow
            if not st.session_state['run']:
                st.session_state['run_id'] = workflow.startWorkflow(**glourbmetrics_params)
                st.session_state['run'] = True

            all_properties = [
            'DATE',
            'AC_AREA',
            'CLOUD_SCORE',
            'COVERAGE_SCORE',
            'DATE_ACQUIRED',
            'DGO_FID',
            'MEAN_AC_MNDWI',
            'MEAN_AC_NDVI',
            'MEAN_MNDWI',
            'MEAN_NDVI',
            'MEAN_VEGETATION_MNDWI',
            'MEAN_VEGETATION_NDVI',
            'MEAN_WATER_MNDWI',
            'VEGETATION_AREA',
            'VEGETATION_PERIMETER',
            'WATER_AREA',
            'WATER_PERIMETER']

            selected_properties = st.multiselect('Select properties', all_properties, default=all_properties)
            st.write('The properties you selected :')
            st.write(selected_properties)

            
            self.task = st.button('Check the advancement of the tasks') 
            if self.task:
                eef.workflowState(st.session_state['run_id'])

            self.get_results = st.button('Get results')
            st.session_state['get_results'] = self.get_results

            if st.session_state['run'] and st.session_state['get_results'] :
                eef.getResults(st.session_state['run_id'], selected_properties, self.ee_project_name, st.session_state['tempdir'])
                st.session_state['run'] = self.get_results

    
if __name__ == "__main__":
    if st.session_state['authenticated'] == True : 
        if st.session_state['dgo_assetId'] == None :
            st.write('You need to load your dgos first :blush:')
        else : 
            pageTwo = PageTwo(st.session_state)
            pageTwo.show()
    else : 
        st.write('Please authenticate :blush:')
    