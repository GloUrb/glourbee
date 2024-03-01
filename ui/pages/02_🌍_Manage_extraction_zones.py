"""
Page of the interface for uploading extraction zones
"""

import streamlit as st
import ee
import os
import geemap.foliumap as geemap

from ee.ee_exception import EEException

from sqlalchemy.sql import text
from glourbee import (
    ui,
    assets_management
)

ui.addHeader('Manage extraction zones')

if not st.session_state['authenticated']:
    st.switch_page('pages/01_🕶️_Authentication.py')


if not st.session_state['extraction_zones']['assetId']:
    assets = st.session_state['db'].query('select * from glourbassets', ttl=0)

    st.title('Select already uploaded extraction zones')
    selection = ui.select_zones(assets, key='selector')

    if len(selection) == 1:
        st.session_state['extraction_zones']['assetId'] = selection['asset_id'].iloc[0]
        st.session_state['extraction_zones']['tableId'] = selection['id'].iloc[0]
        st.session_state['extraction_zones']['features'] = ee.FeatureCollection(st.session_state['extraction_zones']['assetId'])
        st.rerun()

else:
    st.success(f'Selected asset: {st.session_state["extraction_zones"]["assetId"]}')

    if st.button('Unselect asset'):
        st.session_state['extraction_zones']['assetId'] = None
        st.session_state['extraction_zones']['tableId'] = None
        st.session_state['extraction_zones']['features'] = None
        st.rerun()

    map = geemap.Map()
    map.addLayer(st.session_state['extraction_zones']['features'], name='Extraction Zones')
    map.center_object(st.session_state['extraction_zones']['features'])
    map.add_labels(
        st.session_state['extraction_zones']['features'],
        "ZONE_FID",
        font_size="12pt",
        font_color="black",
        font_family="arial",
        font_weight="bold",
    )
    
    map.addLayerControl()  

    map.to_streamlit()


st.title('Upload new extraction zones')
st.warning("Please reuse already uploaded extraction zones if possible to avoid duplication of referentials")

with st.form('upload_new'):
    river_name = st.text_input('Extraction zones name', max_chars=50, help = 'If you are uploading extraction zones for anything else than a river, name correctly so other GloUrbEE users can find it')
    description = st.text_area('Extraction zones description', max_chars=100, help = 'Describe your extraction zones: for example, the ZONEs creation method')
    zones_size = st.number_input('ZONE size (in meters, if applies)', help='If you are uploading extraction zones for anything else than a river, just let a zero here')
    zone_file = st.file_uploader('Extraction zones file', type=['gpkg', 'shp', 'shx', 'dbf', 'prj', 'cpg'], accept_multiple_files=True)

    submitted = st.form_submit_button('Upload to GEE')
    if submitted:
        validate = True
        if not river_name:
            st.error('You need to specify river name')
            validate = False
        if not zone_file:
            st.error('You need to specify extraction zones file')
            validate = False
        
        if validate:
            local_file = []

            for file in zone_file:
                file_path = os.path.join(st.session_state['tempdir'].name, file.name)

                if os.path.splitext(file.name)[1].lower() in ['.gpkg', '.shp']:
                    local_file.append(file_path)
                with open(file_path, 'wb') as temp_file:
                    temp_file.write(file.read())
            
            if len(local_file) != 1:
                st.error('Please provide only one **shp** or one **gpkg** file')
            else:
                with st.spinner("Uploading asset... Don't close this window"):
                    zones_assetId, zones_features = assets_management.uploadExtractionZones(
                        local_file[0], 
                        ee_project_name='ee-glourb', 
                        simplify_tolerance=5)
                    
                    st.session_state['extraction_zones']['features'] = zones_features
                    st.session_state['extraction_zones']['assetId'] = zones_assetId

                    with st.session_state['db'].session as session:
                        session.execute(text("INSERT INTO glourbassets (river_name, zones_size, asset_id, uploader, description) \
                                             VALUES (:r, :d, :a, :u, :des);"),
                                        {'r': river_name,
                                        'd': zones_size,
                                        'a': zones_assetId,
                                        'u': st.session_state['user'],
                                        'des': description})
                        session.commit()

                st.rerun()
        

st.title('Delete extraction zones')

if st.session_state['extraction_zones']['assetId']:
    st.warning('Unselect extraction zones before deleting assets')
    
else:
    assets = st.session_state['db'].query('select * from glourbassets where uploader = :user', 
                                        params={'user': st.session_state['user']},
                                        ttl=0) 
    
    if len(assets) == 0:
        st.warning('No asset to delete')
    else:
        st.warning('You are about to delete a extraction zones asset and all the metrics calculated with it. This is not reversible')
        #TODO: Delete metrics associated with asset

        selection = ui.select_zones(assets, key='deletor')

        if len(selection) == 1:

            try:
                ee.data.deleteAsset(selection['asset_id'].iloc[0])

                with st.session_state['db'].session as session:
                    session.execute(text("DELETE FROM glourbassets WHERE asset_id = :i;"),
                                    {'i': selection['asset_id'].iloc[0]})
                    session.commit()
                
                st.rerun()

            except EEException as e:
                st.write('The asset seems to be already deleted from GEE:')
                st.write(e)
                if st.button('Delete from database'):
                    with st.session_state['db'].session as session:
                        session.execute(text("DELETE FROM glourbassets WHERE asset_id = :i;"),
                                        {'i': selection['asset_id'].iloc[0]})
                        session.commit()
                    
                    st.rerun()
