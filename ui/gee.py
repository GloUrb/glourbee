import os
import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap

from sqlalchemy import text
from glourbee.worker import gee_process

conn = st.connection("postgresql", "sql", url=os.environ['GLOURBEE_DB_URI'])

st.header('Google Earth Engine processing', divider=True)
st.info('This module allows programming the calculation of indicators and masks used for the GloUrb project, and initiating the download of data from Google Earth Engine to this GloUrbEE server.')

if "selected_aoi" not in st.session_state.keys() or not st.session_state['selected_aoi']:
    st.page_link(page='extraction.py', label='Please select extraction zones before', icon="🌍")
    st.stop()


aoi_db = gpd.read_postgis(text("select * from aoi where fid=:fid"), con=conn.connect(), params={'fid': int(st.session_state["selected_aoi"])}, crs=3857, geom_col="geometry")

m = leafmap.Map(center=(45.7326672, 4.8372539))
if len(aoi_db) > 0:
    m.add_gdf(aoi_db.to_crs(4326), layer_name="Area of interest", info_mode=None, style={"color": "gray"})
    m.zoom_to_gdf(aoi_db.to_crs(4326))

st.title("Available data for selected zones")
st.info("Here, you can check and download locally the images that have already been processed on Google Earth Engine and transferred to this GloUrbEE server.")
st.date_input("Selected date range", value=("2025-01-01", "today"), min_value="1980-01-01", max_value="today")
m.to_streamlit()


st.title("Start new data calculation and download")
st.info('Here, you can launch the calculation of masks and indicators for new images using Google Earth Engine. Please note that changing something from the default cloud and masks parameters will make the calculated data only available for you (not the other users) and for 1 month long instead of 6.')

with st.form('gee_process'):
    col1, col2 = st.columns(2)

    form_daterange = st.date_input('Calculated date range', value=("2025-01-01", "today"), min_value="1980-01-01", max_value="today")

    
    col1, col2 = st.columns(2)
    cloud_filter= col1.slider('Cloud filter', min_value= 0, max_value= 100, value = 80, help="Maximum cloud coverage accepted at the image scale")
    cloud_masking = col1.toggle('Cloud masking', value = True, help="Mask the clouds on the results (recommended)")
    # mosaic_same_day = col1.toggle('Mosaic same day', value = True)

    satellite_type = col2.radio('Satellite imagery dataset', 
                                options=['Landsat', 'Sentinel-2'], 
                                captions = ['Data available since 1982-08-22', 'Data available since 2017-03-28'])
    
    ct = st.container(border=1)
    ct.write('Advanced options')
    watermask_expression = ct.text_input('Watermask expression', value="MNDWI >  0.0")
    activechannel_expression = ct.text_input('Active Channel expression', value="NDWI > -0.4 && NDVI < 0.2")
    vegetation_expression = ct.text_input('Vegetation expression', value="NDVI > 0.15")

    if st.form_submit_button("Start tasks"):
        with st.spinner('Starting tasks...'):
            gee_process.delay(
                aoi_fid=int(st.session_state['selected_aoi']),
                date_range=(str(form_daterange[0]), str(form_daterange[1])),
                cloud_filter=cloud_filter,
                cloud_masking=cloud_masking,
                satellite_type=satellite_type,
                watermask_expression=watermask_expression,
                activechannel_expression=activechannel_expression,
                vegetation_expression=vegetation_expression
            )
        

        st.success('Tasks started. Check your task manager to track progress')
        st.balloons()