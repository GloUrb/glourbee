"""
Page of the interface for uploading extraction zones
"""

import streamlit as st
import ee
import os
import geemap.foliumap as geemap

from glourbee import (
    ui,
    assets_management,
    collection
)

ui.addHeader('Manage extraction zones')

if not st.session_state['authenticated']:
    st.switch_page('pages/01_🕶️_Authentication.py')

st.title('Select GloUrbEE extraction zones')

if "assets" not in st.session_state:
    with st.spinner('Loading assets from Earth Engine...'):
        st.session_state.assets = collection.getGlourbeeExtractionZones()


select_zones = st.dataframe(
    st.session_state.assets,
    key="asset_uuid",
    on_select="rerun",
    selection_mode="single-row",
    hide_index=True,
    column_config={
        "asset_uuid": "UUID",
        "metrics_ds": "Number of metrics datasets",
        "zones_author": "Author",
        "description": "Description",
        "len": "Number of polygons",
        "name": "Name",
        "fid_field": "Unique identifier field",
        "type": "Type",
    }
)

if len(select_zones.selection.rows) == 1:
    st.session_state['extraction_zones'] = st.session_state.assets.iloc[select_zones.selection.rows[0]]
    st.session_state['zones_dataset'] = assets_management.ExtractionZones(
        asset_uuid=st.session_state['extraction_zones']['asset_uuid'])
else:
    st.session_state['extraction_zones'] = None

    if 'metrics_info' in st.session_state:
        st.session_state['metrics_info'] = None
        st.session_state['metrics_dataset'] = None

if "extraction_zones" in st.session_state and st.session_state['extraction_zones'] is not None:
    st.success(
        f'Selected asset: {st.session_state["extraction_zones"]["name"]} ({st.session_state["extraction_zones"]["asset_uuid"]})')
    

    if st.button(':red[Delete selected asset (irreversible)]'):
        if st.button('WARNING: IRREVERSIBLE OPERATION. ARE YOU SURE?', type='primary'):
            st.session_state['zones_dataset'].cancel_linked_tasks()
            st.session_state['zones_dataset'].delete()
            st.session_state['extraction_zones'] = None

            st.session_state.assets = collection.getGlourbeeExtractionZones()
            st.rerun()


    current_state = st.session_state['zones_dataset'].gee_state

    if current_state != 'complete':
        st.warning(
            f'This asset is not completely uploaded ({current_state}). Please wait until the upload is finished.', icon="🚨")
    else:
        st.session_state['extraction_zones']['features'] = ee.FeatureCollection([ee.Feature(ee.FeatureCollection(
            asset['id']).first()) for asset in st.session_state['zones_dataset'].gee_assets])

        map = geemap.Map()
        map.addLayer(st.session_state['extraction_zones']['features'], name='Extraction Zones')
        map.center_object(st.session_state['extraction_zones']['features'])
        map.add_labels(
            st.session_state['extraction_zones']['features'],
            st.session_state['extraction_zones']['fid_field'],
            font_size="12pt",
            font_color="black",
            font_family="arial",
            font_weight="bold",
        )

        map.addLayerControl()

        map.to_streamlit()


st.title('Upload new extraction zones to GloUrbEE collection')
st.warning("Please reuse already uploaded extraction zones if possible to avoid duplication of referentials")

with st.form('upload_new'):
    zones_type = st.text_input('Extraction zones type', max_chars=50,
                               help='Literal description of the zones types (eg. DGOs, Cites, Gravel quarries, ...)')
    description = st.text_area('Extraction zones description', max_chars=100,
                               help='Literal description of the zones. Give a maximum details so other GloUrb researcher can understand chat are these zones.')
    fid_field = st.text_input('Unique identifier Field', max_chars=50,
                              help='Field name that contains the unique identifier of each zone.')
    author = st.text_input(
        'Author', max_chars=50, help='Identify the producer of those extraction zones.', value=st.session_state['user'])
    zone_file = st.file_uploader('Extraction zones file', type=[
                                 'gpkg', 'shp', 'shx', 'dbf', 'prj', 'cpg'], accept_multiple_files=True)

    submitted = st.form_submit_button('Upload to GloUrbEE collection')

    if submitted:
        validate = True

        if not zones_type:
            st.error('You need to specify extraction zones type')
            validate = False

        if not zone_file:
            st.error('You need to specify extraction zones file')
            validate = False

        if not description:
            st.error('You need to specify extraction zones description')
            validate = False

        if not fid_field:
            st.error('You need to specify the unique identifier field')
            validate = False

        if not author:
            st.error('You need to specify the author of the extraction zones')
            validate = False

        if validate:
            local_file = []

            for file in zone_file:
                file_path = os.path.join(
                    st.session_state['tempdir'].name, file.name)

                if os.path.splitext(file.name)[1].lower() in ['.gpkg', '.shp']:
                    local_file.append(file_path)
                with open(file_path, 'wb') as temp_file:
                    temp_file.write(file.read())

            if len(local_file) != 1:
                st.error('Please provide only one **shp** or one **gpkg** file')
            else:
                with st.spinner("Starting asset upload... Don't close this window"):
                    new_asset = assets_management.ExtractionZones(local_file=local_file[0],
                                                                  fid_field=fid_field,
                                                                  zone_type=zones_type,
                                                                  description=description,
                                                                  author=author
                                                                  )
                    new_asset.upload_to_gee()

                st.rerun()
