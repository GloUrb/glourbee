"""
Page of the interface for uploading extraction zones
"""

import os
import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap

from sqlalchemy import text

conn = st.connection("postgresql", "sql", url=os.environ['GLOURBEE_DB_URI'])
aoi_db = gpd.read_postgis('select * from aoi order by last_access desc', con=conn.connect(), crs=3857, geom_col="geometry").to_crs(epsg=4326)
zone_db = gpd.read_postgis('select * from zone', con=conn.connect(), crs=3857, geom_col="geometry").to_crs(epsg=4326)

st.header('Manage GloUrbEE extraction zones', divider=True)
st.info('This module allows you to explore, add, or remove new extraction areas on this GloUrbEE server. All users areas are shared, but you can only delete those that belong to you.')

m = leafmap.Map(center=(45.7326672, 4.8372539))
if len(aoi_db) > 0:
    m.add_gdf(zone_db, layer_name="Extraction zones", info_mode=None)
    m.add_gdf(aoi_db, layer_name="Areas of interest", style={"color": "black"})
    m.zoom_to_gdf(aoi_db)

st.title(f'Existing extraction zones on this GloUrbEE server')

if len(aoi_db) == 0:
    st.warning('Nothing to see here')
else:
    zones_table = st.dataframe(aoi_db[["fid", "type", "description", "author", "last_access"]], hide_index=True, on_select="rerun", selection_mode="single-row", 
                            column_config={
                                "fid": st.column_config.NumberColumn("FID", help="Unique identifier for this zones"),
                                "type": st.column_config.TextColumn("Type", help="Literal description of the zones types"),
                                "description": st.column_config.TextColumn("Description", help="Literal description of the zones."),
                                "author": st.column_config.TextColumn("Author", help="Uploader"),
                                "last_access": st.column_config.DatetimeColumn("Last access", help="Zones unused more than 3 month are automatically purged"),
                                "geometry": None
                            })

    if len(zones_table.selection.rows) == 1:
        selected_gdf = aoi_db.iloc[zones_table.selection.rows]
        selected_zone = selected_gdf.iloc[0]
        m.add_gdf(selected_gdf, style={"color": "red"}, info_mode=None)
        m.zoom_to_gdf(selected_gdf)

        st.session_state["selected_aoi"] = selected_zone["fid"]

        owned = selected_zone["author"] == st.session_state["user"]["name"]
        with st.popover("Delete selected", icon='🗑️', disabled = not owned, help="You can only delete the dataset from which you are the author"):
            st.warning("This will delete the selected zones and all data associated on this GloUrbEE server", icon='🚨')
            if st.button("Confirm"):
                with st.spinner("Deleting..."):
                    with conn.session as session:   
                        session.execute(text('delete from zone cascade where aoi_fid=:fid;'), {"fid": int(selected_zone["fid"])})
                        session.execute(text('delete from aoi cascade where fid=:fid;'), {"fid": int(selected_zone["fid"])})
                        session.commit()
                
                st.rerun()
    
    else:
        st.session_state["selected_aoi"] = None

m.to_streamlit()

st.title('Upload new extraction zones')

with st.form('upload_new'):
    zones_type = st.text_input('Extraction zones type', max_chars=50,
                               help='Literal description of the zones types (eg. DGOs, Cites, Gravel quarries, ...)', )
    description = st.text_area('Extraction zones description', max_chars=100,
                               help='Literal description of the zones. Give a maximum details so other GloUrb researcher can understand what are these zones about.')
    fid_field = st.text_input('Unique identifier Field', max_chars=50,
                              help='Field name that contains the unique identifier of each zone.')
    author = st.text_input(
        'Author', max_chars=50, help='Identify the producer of those extraction zones.', value=st.session_state['user']['name'], disabled=True)
    zone_file = st.file_uploader('Extraction zones file', type=[
                                 'gpkg', 'zip'], accept_multiple_files=False, help="Please zip shapefiles with all their side files.")

    upload_form = st.form_submit_button('Upload to GloUrbEE collection')

if upload_form:
    validate = True

    if not zones_type:
        st.error('Please specify extraction zones type')
        st.stop()
    if not zone_file:
        st.error('Please specify extraction zones file')
        st.stop()
    if not description:
        st.error('Please specify extraction zones description')
        st.stop()
    if not fid_field:
        st.error('Please specify the unique identifier field')
        st.stop()
    if not author:
        st.error('Please specify the author of the extraction zones')
        st.stop()

    try:
        uploaded_gdf = gpd.read_file(zone_file.read())
        uploaded_gdf.to_crs(epsg=3857, inplace=True)
    except:
        st.error("Unable to read and project your vector file.")
        st.stop()

    with st.spinner("Uploading..."):
        aoi = uploaded_gdf[["geometry"]].dissolve().simplify(10)
        aoi['author'] = author
        aoi['type'] = zones_type
        aoi['description'] = description

        aoi.to_postgis(name='aoi', con=conn.connect(), if_exists='append')

        df = conn.query('select * from aoi where author=:author and type=:type and description=:description order by last_access desc limit 1',
                params={
                    "author": author,
                    "type": zones_type,
                    "description": description
                }, ttl=5)
        aoi_fid = df.loc[0]['fid']

        uploaded_gdf['aoi_fid'] = aoi_fid
        uploaded_gdf['zone_fid'] = uploaded_gdf[fid_field]
        zones = uploaded_gdf[["aoi_fid", "zone_fid", "geometry"]].simplify(10)

        zones.to_postgis(name='zone', con=conn.connect(), if_exists='append')

        st.rerun()
