""" Page for choosing the metrics in the interface
"""
import streamlit as st
import os
import geopandas as gpd
import time

from celery import chord
from sqlalchemy import text
from glourbee.worker import calculate_metrics, aggregate_metrics

conn = st.connection("postgresql", "sql", url=os.environ['GLOURBEE_DB_URI'])

st.header('Metrics extraction', divider=True)
st.info('This module extracts the statistical distribution of each indice and calculated mask by Google Earth Engine (GEE) at the scale of each extraction zone. ' \
'The output format is a the GloUrbEE metrics dataframe.')

if "selected_aoi" not in st.session_state.keys() or not st.session_state['selected_aoi']:
    st.page_link(page='extraction.py', label='Please select extraction zones before', icon="🌍")
    st.stop()

if "selected_images" not in st.session_state.keys() or len(st.session_state['selected_images'].query('processed==True')) == 0:
    st.page_link(page='gee.py', label='Please select images before', icon="🌍")
    st.write('Only fully processed images (blue footprints) are considered')
    st.stop()

zone_db: gpd.GeoDataFrame = gpd.read_postgis(text("select * from zone where aoi_fid=:fid"), con=conn.connect(), params={'fid': int(st.session_state["selected_aoi"])}, crs=3857, geom_col="geometry")
images_to_process = st.session_state['selected_images'].query('processed==True')

st.write(f'Metrics will be extracted on **{len(zone_db)}** extraction zones over **{len(images_to_process)}** satellite images \
         from **{min(images_to_process['date'])}** to **{max(images_to_process['date'])}**')

with st.form('calculate_metrics'):
    email = st.text_input("Email notification", value=None, help="Get an email notification when your process is completed")

    if st.form_submit_button('Start extraction'):

        output_csv = os.path.join(os.environ['GLOURBEE_DATASTORE'], 
                                  'metrics', 
                                  f'{st.session_state['user']['name']}_{time.strftime("%Y%m%d-%H%M%S")}.csv')
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)

        header = [calculate_metrics.s(int(i), int(st.session_state['selected_aoi'])) for i in list(images_to_process['fid'])]
        callback = aggregate_metrics.s(output_csv, email)
        chord(header)(callback)

        st.balloons()
        st.toast('Tasks started. You will receive an email when your metrics are ready', icon='🚀')
