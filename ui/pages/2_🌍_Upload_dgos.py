"""Page of the interface for uploading dgos

"""

import streamlit as st
import ee_interface_function as eef
import ee
import folium
import os
from streamlit_folium import folium_static

current_directory = os.getcwd()
cities_data = eef.cities(f'{current_directory}\cities.txt')

class PageOne:
    """PageOne class to show the Upload dgos page of the app 

    gives different options for loading dgos, uploading to Earth Engine or getting them from it.
    Shows a map centered on them

    """
    def __init__(self, session_state):
        self.title = "Upload DGOs"
        self.shp_file = None
        self.ee_project_name = "ee-glourb"
        self.dgo_features = None
        self.session_state = session_state
        self.cities_data = eef.cities('cities.txt')
        self.list_cities = list(self.cities_data.keys())
        self.id = None
        self.map_container = st.empty() 
        self.feature_group = folium.FeatureGroup(name='DGO Features')
        self.town = None
        self.river = None
        self.matching_lines = None
        self.action = None

    def update_map(self):
        location = [self.cities_data[self.town]["latitude"], self.cities_data[self.town]["longitude"]]
        m = folium.Map(location=location, zoom_start=8, title='DGO map')

        features = self.session_state['dgo_features']
        if features:
            folium.GeoJson(data=features.getInfo()).add_to(self.feature_group)
            self.feature_group.add_to(m)

        folium_static(m)

    def show(self):
        print(f'current directory : {current_directory}')
        image_path = f'{current_directory}\logo.svg'
        st.image(image_path,  use_column_width=True, width=5)

        st.title(self.title)
        st.write('Here you can upload your DGOs or get them directly from GEE is they\'ve already been uploaded as assets (this is faster)')

        self.town = st.selectbox('Town', self.list_cities, help = 'Choose the town you are working on')
        self.river = st.text_input('River', help = 'The name of your river')

        if self.river:
            self.matching_lines, self.matching_times = eef.dgo_to_search(self.town, self.river)
            if len(self.matching_lines) != 0:
                st.write('Here are the dgos already loaded in GEE as assets for the same town or river:')
                for i in range(len(self.matching_lines)):
                    st.markdown(f'<span style="color:green">{i+1}</span>- id of the asset : {self.matching_lines[i]} \ update time = {self.matching_times[i]}', unsafe_allow_html=True)
                st.write('Select an action:')
                self.action = st.selectbox('Choose an action:', ['Choose an action', 'Use already uploaded DGOs', 'Upload my own DGOs'] , help = 'You can use an asset already uploaded (from the list above) or upload your own !')

                if self.action == 'Use already uploaded DGOs':
                    if len(self.matching_lines) > 1:
                        i = st.number_input('Number of the asset you want from the list above', 1, len(self.matching_lines), step=1, value = None)
                        if i is not None:
                            self.id = self.matching_lines[i - 1]
                            st.write(f'You\'re using the asset number {i} with the id: {self.id}')
                            
                            self.session_state['dgo_assetId'] = self.id
                            self.session_state['dgo_features'] = ee.FeatureCollection(self.id)

                    elif len(self.matching_lines) == 1:
                        i = 1
                        
                    else:
                        i = None

                elif self.action == 'Upload my own DGOs':
                    st.write('Do you want to replace an already loaded asset? (in order to not overcrowd the server)')
                    replace_asset = st.radio('Choose an option:', ['Yes', 'No'])

                    if replace_asset == 'Yes':
                        if len(self.matching_lines) > 1:
                            i = st.number_input('Number of the asset you want to remove', 1, len(self.matching_lines), step=1)
                            id_to_remove = self.matching_lines[i - 1]
                            update_time = self.matching_lines[i - 1]
                        elif len(self.matching_lines) == 1:
                            i = 1
                            id_to_remove = self.matching_lines[i - 1]
                            update_time = self.matching_lines[i - 1]
                        else:
                            i = None

                        if i is not None:
                            st.write(f'You\'re removing the asset number {i} with the id: {id_to_remove}')
                            if st.button('Confirm'):
                                eef.remove_line_by_criteria(id_to_remove)
                                st.markdown('<span style="color:green">Thanks for keeping the server clean !</span> :grin:' , unsafe_allow_html=True)
                                st.write('Let\'s now load the dgos !')
                                st.write('Keep in mind that this is going to take time :sweat_smile:')
                                self.shp_file = st.file_uploader("Upload Shape file", accept_multiple_files = True, help = 'Here you can upload your dgos, meaning the .shp of course but also the .shx, .cpg, .dbf, .prj and .qmd')

                    elif replace_asset == 'No':
                        self.shp_file = st.file_uploader("Upload Shape file", accept_multiple_files = True)

            else : 
                self.shp_file = st.file_uploader("Upload Shape file", accept_multiple_files = True)

        if self.shp_file:
            import os
            st.write(self.shp_file) 
            from glourbee import assets_management
            import geopandas as gpd

            dgo_shapefile = self.shp_file
            temp_dir = "./temp"
            os.makedirs(temp_dir, exist_ok=True)

            file_paths = {}
            for file in dgo_shapefile:
                file_path = os.path.join(temp_dir, file.name)
                with open(file_path, 'wb') as temp_file:
                    temp_file.write(file.read())
                file_paths[file.name] = file_path

            self.dgo_assetId, self.dgo_features = assets_management.uploadDGOs(file_paths['Yamuna_segm_2km_UTF8.shp'],  ee_project_name=self.ee_project_name, simplify_tolerance=15)

            for file_path in file_paths.values():
                os.remove(file_path)

            self.session_state['dgo_features'] = self.dgo_features
            self.session_state['dgo_assetId'] = self.dgo_assetId

        self.update_map()

if __name__ == "__main__":        
    pageOne = PageOne(st.session_state)
    if st.session_state['authenticated'] == True : 
        pageOne.show()
    else : 
        st.write('Please authenticate :blush:')