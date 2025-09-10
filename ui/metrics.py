""" Page for choosing the metrics in the interface
"""
import streamlit as st
import os
import pandas as pd
import geopandas as gpd

from sqlalchemy import text
from glourbee import zones_metrics
# from rasterstats import zonal_stats

from importlib import reload
reload(zones_metrics)

conn = st.connection("postgresql", "sql", url=os.environ['GLOURBEE_DB_URI'])

st.header('Metrics extraction', divider=True)
st.info('This module extracts the statistical distribution of each indicator and calculated mask by Google Earth Engine (GEE) at the scale of each extraction zone. ' \
'The output format is a the GloUrbEE metrics dataframe.')

if "selected_aoi" not in st.session_state.keys() or not st.session_state['selected_aoi']:
    st.page_link(page='extraction.py', label='Please select extraction zones before', icon="🌍")
    st.stop()

if "selected_images" not in st.session_state.keys() or len(st.session_state['selected_images']) == 0:
    st.page_link(page='gee.py', label='Please select images before', icon="🌍")
    st.write('Only fully processed images (blue footprints) are considered')
    st.stop()

zone_db: gpd.GeoDataFrame = gpd.read_postgis(text("select * from zone where aoi_fid=:fid"), con=conn.connect(), params={'fid': int(st.session_state["selected_aoi"])}, crs=3857, geom_col="geometry")

                                 
# st.write()
# st.write('Please review selected images and extraction zones first')
# st.dataframe(st.session_state['selected_images'])
# st.dataframe(zone_db)

st.write(f'Metrics will be extracted on **{len(zone_db)}** extraction zones over **{len(st.session_state['selected_images'])}** satellite images \
         from **{min(st.session_state['selected_images']['date'])}** to **{max(st.session_state['selected_images']['date'])}**')

@st.cache_data
def convert_for_download(df):
    return df.to_csv().encode("utf-8")

if st.button('Start extraction'):
    output_metrics = list()

    progress = st.progress(0, text='Metrics extraction (started)')

    for n, i in st.session_state['selected_images'].iterrows():
        local_zones = zone_db[zone_db.intersects(i.geometry)]
        local_zones['image'] = i['name']
        local_zones['date'] = i['date']
        local_zones['satellite'] = i['satellite']

        #TODO: paralleliser avec pandas
        # for _, z in local_zones.iterrows():
        #     r = zones_metrics.calculcateZONEsMetricsLocal(i['path'], z['geometry'])

        r = local_zones.apply(lambda row: zones_metrics.calculcateZONEsMetricsLocal(i['path'], row['geometry']), axis=1, result_type='expand')
        local_zones = pd.concat([local_zones, r], axis=1)

        output_metrics.append(local_zones.drop(['fid', 'geometry'], axis=1))

        p = n/(len(st.session_state['selected_images'])-1)
        progress.progress(p, text=f'Metrics extraction ({int(p*100)}%)')

    progress.progress(1.0, text='Metrics extraction (done)')
    output_metrics = pd.concat(output_metrics)

    csv = convert_for_download(output_metrics)
    st.download_button('Download csv', csv, file_name="glourbee_metrics.csv", mime="text/csv", icon=":material/download:")

    st.dataframe(output_metrics)
