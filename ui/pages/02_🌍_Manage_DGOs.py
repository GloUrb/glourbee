"""Page of the interface for uploading dgos

"""

import streamlit as st
import ee
import os
import geemap.foliumap as geemap

from sqlalchemy.sql import text
from glourbee import (
    ui,
    assets_management
)

ui.addHeader('Manage DGOs')

if not st.session_state['authenticated']:
    st.switch_page('pages/01_🕶️_Authentication.py')


if not st.session_state['dgo_assetId']:
    assets = st.session_state['db'].query('select * from glourbassets', ttl=60)

    st.title('Select already uploaded DGOs')
    selection = ui.select_dgos(assets)

    if len(selection) == 1:
        st.session_state['dgo_assetId'] = selection['asset_id'].iloc[0]
        st.session_state['dgo_table_id'] = selection['id'].iloc[0]
        st.session_state['dgo_features'] = ee.FeatureCollection(st.session_state['dgo_assetId'])
        st.rerun()

else:
    st.success(f'Selected asset: {st.session_state["dgo_assetId"]}')

    if st.button('Unselect asset'):
        st.session_state['dgo_assetId'] = None
        st.session_state['dgo_table_id'] = None
        st.session_state['dgo_features'] = None
        st.rerun()

    map = geemap.Map()
    map.addLayer(st.session_state['dgo_features'], name='DGOs')
    map.center_object(st.session_state['dgo_features'])
    map.add_labels(
        st.session_state['dgo_features'],
        "DGO_FID",
        font_size="12pt",
        font_color="black",
        font_family="arial",
        font_weight="bold",
    )
    
    map.addLayerControl()  

    map.to_streamlit()


st.title('Upload new DGOs')
st.warning("Please reuse already uploaded DGOs if possible to avoid duplication of referentials")

with st.form('upload_new'):
    river_name = st.text_input('River name', help = 'If you are uploading DGOs for anything else than a river, name correctly so other GloUrbEE users can find it')
    dgo_size = st.number_input('DGO size (in meters, if applies)', help='If you are uploading DGOs for anything else than a river, just let a zero here')
    dgo_file = st.file_uploader('DGOs file', type=['gpkg', 'shp', 'shx', 'dbf', 'prj', 'cpg'], accept_multiple_files=True)

    submitted = st.form_submit_button('Upload to GEE')
    if submitted:
        validate = True
        if not river_name:
            st.error('You need to specify river name')
            validate = False
        if not dgo_size:
            st.error('You need to specify DGO size')
            validate = False
        if not dgo_file:
            st.error('You need to specify DGO file')
            validate = False
        
        if validate:
            local_file = []

            for file in dgo_file:
                file_path = os.path.join(st.session_state['tempdir'].name, file.name)

                if os.path.splitext(file.name)[1].lower() in ['.gpkg', '.shp']:
                    local_file.append(file_path)
                with open(file_path, 'wb') as temp_file:
                    temp_file.write(file.read())
            
            if len(local_file) != 1:
                st.error('Please provide only one **shp** or one **gpkg** file')
            else:
                with st.spinner("Uploading asset... Don't close this window"):
                    dgo_assetId, dgo_features = assets_management.uploadDGOs(
                        local_file[0], 
                        ee_project_name='ee-glourb', 
                        simplify_tolerance=5)
                    
                    st.session_state['dgo_features'] = dgo_features
                    st.session_state['dgo_assetId'] = dgo_assetId

                    with st.session_state['db'].session as session:
                        session.execute(text("INSERT INTO glourbassets (river_name, dgo_size, asset_id, uploader) VALUES (:r, :d, :a, :u);"),
                                        {'r': river_name,
                                        'd': dgo_size,
                                        'a': dgo_assetId,
                                        'u': st.session_state['user']})
                        session.commit()

                st.rerun()
        

st.title('Delete outdated DGOs')

if st.session_state['dgo_assetId']:
    st.warning('Unselect DGOs before deleting assets')
    
else:
    st.warning('You are about to delete a DGOs asset and all the metrics calculated with it. This is not reversible')
    #TODO: Delete metrics associated with asset

    assets = st.session_state['db'].query('select * from glourbassets where uploader = :user', 
                                        params={'user': st.session_state['user']},
                                        ttl=60) 

    selection = ui.select_dgos(assets)

    if len(selection) == 1:

        ee.data.deleteAsset(selection['asset_id'].iloc[0])

        with st.session_state['db'].session as session:
            session.execute(text("DELETE FROM glourbassets WHERE asset_id = :i;"),
                            {'i': selection['asset_id'].iloc[0]})
            session.commit()
            
        st.rerun()
