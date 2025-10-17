import os
import re
import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap

from time import sleep
from sqlalchemy import text
from glourbee.worker import gee_process, upload_archive

conn = st.connection("postgresql", "sql", url=os.environ['GLOURBEE_DB_URI'])

st.header('Google Earth Engine processing', divider=True)
st.info('This module allows programming the calculation of indices and masks used for the GloUrb project, and initiating the download of data from Google Earth Engine to this GloUrbEE server.')

if "selected_aoi" not in st.session_state.keys() or not st.session_state['selected_aoi']:
    st.page_link(page='extraction.py', label='Please select extraction zones before', icon="🌍")
    st.stop()

# Récupérations des tables en BD
zone_db = gpd.read_postgis(text("select * from zone where aoi_fid=:fid"), con=conn.connect(), params={'fid': int(st.session_state["selected_aoi"])}, crs=3857, geom_col="geometry")
image_db = gpd.read_postgis(text('select image.*, aoi.fid as aoi_fid, aoi.geometry as aoi_geom from image, aoi where aoi.fid=:fid and st_intersects(image.geometry, aoi.geometry) and image.user in (\'all\', :user)'), params={'fid': int(st.session_state["selected_aoi"]), 'user': st.session_state['user']['name']}, con=conn.connect(), crs=3857, geom_col="geometry")
image_db['processed'] = image_db['path'].notnull()

# Cherche l'interval à afficher par défaut
if len(image_db) > 0:
    ival = (min(image_db["date"]), max(image_db["date"]))
else:
    ival = ("2025-01-01", "today")

st.title("Available data for selected zones")
st.info("Here, you can check and download locally the images that have already been processed on Google Earth Engine and transferred to this GloUrbEE server. Gray footprints are currently processing images, blue footprints are images processed and available for local download.")
selected_range = st.date_input("Selected date range", value=ival, min_value="1980-01-01", max_value="today")
# selected_satellites = st.multiselect('Satellite type', ['Landsat', 'Sentinel-2'], default=['Landsat', 'Sentinel-2'])

# Créer la sélection d'images en fonction de l'interval de dates choisi
if len(selected_range) == 2:
    selected_images = image_db[(image_db['date'] >= selected_range[0]) & (image_db['date'] <= selected_range[1])]
    selected_images['date'] = selected_images['date'].astype(str)
    st.session_state['selected_images'] = selected_images.query('processed==True')
else:
    selected_images = list()
    st.session_state['selected_images'] = list()

# Création carte
m = leafmap.Map(center=(45.7326672, 4.8372539), draw_control=False)

# Ajout des footprints si il y a des images dans l'interval
if len(selected_images) > 0:
    
    if selected_images['processed'].any():
        m.add_gdf(selected_images.query('processed==True').to_crs(4326), layer_name="Available images", style={"color": "blue"}, zoom_to_layer=False)
    
    if not selected_images['processed'].all():
        m.add_gdf(selected_images.query('processed==False').to_crs(4326), layer_name="Currently processed images", style={"color": "gray"}, zoom_to_layer=False)

    m.add_labels(selected_images.to_crs(4326), "date", font_color="black", layer_name="Images dates")
    
# Ajout des DGOs
if len(zone_db) > 0:
    m.add_gdf(zone_db.to_crs(4326), layer_name="Selected extraction zones", info_mode=None, style={"color": "red"})
    m.add_labels(zone_db.to_crs(4326), "zone_fid", font_color="red", layer_name="Extraction zones UID")
    m.zoom_to_gdf(zone_db.to_crs(4326))

# Affichage de la carte
m.to_streamlit()

# Bouton de téléchargement si sélection pas vide
with st.popover('Download data corresponding to blue footprints', disabled=len(st.session_state['selected_images'])==0):
    st.write("Creating the archive may take some time. An email with a FileSender link will be sent to you once the archive is ready. Please do not initiate the creation of multiple archives simultaneously.")
    dest = st.text_input('Email', help="The email address where the download link will be send")
    if st.button('Create archive'):
        
        try:
            assert re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', dest)
        except AssertionError:
            st.error('Invalid email format')

        upload_archive.delay(list(st.session_state['selected_images']['path']), dest)

        st.balloons()
        st.success('Archive creation successfully started')
        sleep(2)
        st.rerun()

st.title("Start new data calculation and download")
st.info('Here, you can launch the calculation of masks and indices for new images using Google Earth Engine. Please note that changing something from the default cloud and masks parameters will make the calculated data only available for you (not the other users) and for 1 month long instead of 6.')

@st.fragment
def new_data_form():
    form = st.container(border=1)
    form_daterange = form.date_input('Calculated date range', value=("2025-01-01", "2025-01-31"), min_value="1980-01-01", max_value="today")

    col1, col2 = form.columns(2)
    cloud_filter= col1.slider('Cloud filter', min_value= 0, max_value= 100, value = 80, help="Maximum cloud coverage accepted at the image scale")
    cloud_masking = col1.toggle('Cloud masking', value = True, help="Mask the clouds on the results (recommended)")

    satellite_type = col2.radio('Satellite imagery dataset', 
                                options=['Landsat', 'Sentinel-2'], 
                                captions = ['Data available since 1982-08-22', 'Data available since 2017-03-28'])

    email = form.text_input("Email notification (optional)", value=None, help="Get an email notification when your process is completed")
        
    ct = form.container(border=1)
    ct.write('Advanced options')

    if satellite_type == "Landsat":
        default_water = "MNDWI > 0.0"
        default_ac = "MNDWI > -0.4 && NDVI < 0.2"
        default_veget = "NDVI > 0.15"

    elif satellite_type == "Sentinel-2":
        default_water = "NDWI > -0.1"
        default_ac = "NDWI > -0.4 && NDVI < 0.2"
        default_veget = "NDVI > 0.15"

    watermask_expression = ct.text_input('Watermask expression', value=default_water)
    activechannel_expression = ct.text_input('Active Channel expression', value=default_ac)
    vegetation_expression = ct.text_input('Vegetation expression', value=default_veget)

    if (
            cloud_filter != 80 or
            not cloud_masking or
            watermask_expression != default_water or
            activechannel_expression != default_ac or
            vegetation_expression != default_veget
        ):
        user = st.session_state['user']['name']
    else:
        user = 'all'

    if form.button("Start tasks"):
        with st.spinner('Starting tasks...'):
            gee_process.delay(
                aoi_fid=int(st.session_state['selected_aoi']),
                date_range=(str(form_daterange[0]), str(form_daterange[1])),
                cloud_filter=cloud_filter,
                cloud_masking=cloud_masking,
                satellite_type=satellite_type,
                watermask_expression=watermask_expression,
                activechannel_expression=activechannel_expression,
                vegetation_expression=vegetation_expression,
                user=user,
                email_notif=email
            )
        
        st.balloons()
        st.toast('Tasks started. Check your task manager to track progress', icon='🚀')

new_data_form()