""" Page for choosing the metrics in the interface
"""
import streamlit as st
import os
import pandas as pd
import geopandas as gpd
import numpy as np

from time import sleep
from multiprocessing import cpu_count
from threading import Thread
from sqlalchemy import text
from glourbee import zones_metrics

conn = st.connection("postgresql", "sql", url=os.environ['GLOURBEE_DB_URI'])

import time
class ProcessImage(Thread):
    def __init__(self, img_subset, zone_db):
        super().__init__()
        self.img_subset = pd.DataFrame(img_subset)
        self.zone_db = zone_db
        self.return_value = list()

    def run(self):
        for _, i in self.img_subset.iterrows():
            local_zones = self.zone_db[self.zone_db.intersects(i.geometry)]
            local_zones['image'] = i['name']
            local_zones['date'] = i['date']
            local_zones['satellite'] = i['satellite']

            r = local_zones.apply(lambda row: zones_metrics.calculcateZONEsMetricsLocal(i['path'], row['geometry']), axis=1, result_type='expand')
            local_zones = pd.concat([local_zones, r], axis=1)

            self.return_value.append(local_zones.drop(['fid', 'geometry'], axis=1))

        self.return_value = pd.concat(self.return_value)
        

st.header('Metrics extraction', divider=True)
st.info('This module extracts the statistical distribution of each indice and calculated mask by Google Earth Engine (GEE) at the scale of each extraction zone. ' \
'The output format is a the GloUrbEE metrics dataframe.')

if "selected_aoi" not in st.session_state.keys() or not st.session_state['selected_aoi']:
    st.page_link(page='extraction.py', label='Please select extraction zones before', icon="🌍")
    st.stop()

if "selected_images" not in st.session_state.keys() or len(st.session_state['selected_images']) == 0:
    st.page_link(page='gee.py', label='Please select images before', icon="🌍")
    st.write('Only fully processed images (blue footprints) are considered')
    st.stop()

zone_db: gpd.GeoDataFrame = gpd.read_postgis(text("select * from zone where aoi_fid=:fid"), con=conn.connect(), params={'fid': int(st.session_state["selected_aoi"])}, crs=3857, geom_col="geometry")

st.write(f'Metrics will be extracted on **{len(zone_db)}** extraction zones over **{len(st.session_state['selected_images'])}** satellite images \
         from **{min(st.session_state['selected_images']['date'])}** to **{max(st.session_state['selected_images']['date'])}**')

@st.cache_data
def convert_for_download(df):
    return df.to_csv().encode("utf-8")
    
if st.button('Start extraction'):

    nproc = int(cpu_count()/2) if int(cpu_count()/2) < len(st.session_state['selected_images']) else len(st.session_state['selected_images'])

    progress = st.progress(0, text='Metrics extraction (started)')
    subsets = np.array_split(st.session_state['selected_images'], nproc)

    threads = [ProcessImage(img_subset, zone_db) for img_subset in subsets]
    for thread in threads:
        thread.start()

    thread_alive = [t.is_alive() for t in threads]
    while any(thread_alive):
        thread_alive = [t.is_alive() for t in threads]
        p = sum([not alive for alive in thread_alive])/len(thread_alive)

        progress.progress(p, text=f"Metrics extraction ({int(p*100)}%)")
        sleep(0.5)

    output_metrics = pd.concat([t.return_value for t in threads])

    csv = convert_for_download(output_metrics)
    st.download_button('Download CSV', csv, file_name=f"glourbee_metrics_{st.session_state["selected_aoi"]}.csv", mime="text/csv", icon=":material/download:")

    st.dataframe(output_metrics)
