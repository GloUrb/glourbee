import os
import ee
import geemap
import geopandas as gpd
import json
import smtplib
import re

from subprocess import call
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
from contextlib import redirect_stdout
from email.mime.text import MIMEText
from datetime import datetime
from sqlalchemy import text, create_engine, bindparam
from celery import Celery
from shapely.geometry import shape, Polygon

app = Celery('glourbee-worker', 
             broker=os.environ['GLOURBEE_BROKER_URL'],
             backend=os.environ['GLOURBEE_BROKER_URL'])

engine = create_engine(os.environ['GLOURBEE_DB_URI'])


def email_notification(email: str, message: str, success: bool=True):

    assert re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

    message = MIMEText(f'Your GloUrbEE processing has finished with the following {'success' if success else 'fail'} message: \n\
                       {message}')
    message['From'] = os.environ['GLOURBEE_EMAIL_FROM']
    message['To'] = email
    message['Subject'] = f'[GloUrbEE] {'Success' if success else 'Fail'} notification'
    mail_server = smtplib.SMTP(host=os.environ['GLOURBEE_EMAIL_SERVER'], port=os.environ['GLOURBEE_EMAIL_PORT'])
    mail_server.login(os.environ['GLOURBEE_EMAIL_USER'], os.environ['GLOURBEE_EMAIL_PASSWORD'])
    mail_server.send_message(message)
    mail_server.quit()


@app.task
def gee_process(aoi_fid: int,
                date_range: tuple[str, str], 
                cloud_filter: int = 80, 
                cloud_masking: bool = True, 
                satellite_type: str = "Landsat", 
                watermask_expression: str = "MNDWI >  0.0", 
                activechannel_expression: str = "NDWI > -0.4 && NDVI < 0.2", 
                vegetation_expression: str = "NDVI > 0.15",
                user: str='all',
                email_notif: str=None):
    
    assert satellite_type in ['Landsat', 'Sentinel-2']

    with open(os.environ['GLOURBEE_EE_JSONKEY']) as f:
        ee_json_key = json.load(f)
    credentials = ee.ServiceAccountCredentials(email=ee_json_key['client_email'], key_data=json.dumps(ee_json_key))
    ee.Initialize(credentials)

    from glourbee import data_management, classification

    aoi_gdf = gpd.read_postgis(text("select * from aoi where fid=:fid"), con=engine, params={'fid': aoi_fid}, crs=3857, geom_col="geometry")

    aoi_fc = geemap.gdf_to_ee(aoi_gdf)

    if satellite_type == "Landsat":
        collection = data_management.getLandsatCollection(start=ee.Date(date_range[0]), 
                                                        end=ee.Date(date_range[1]), 
                                                        cloud_filter=cloud_filter,
                                                        cloud_masking=cloud_masking,
                                                        mosaic_same_day=False, 
                                                        roi=aoi_fc.first().geometry())
    elif satellite_type == "Sentinel-2":
        collection = data_management.getSentinelCollection(start=ee.Date(date_range[0]), 
                                                        end=ee.Date(date_range[1]), 
                                                        cloud_filter=cloud_filter,
                                                        cloud_masking=cloud_masking,
                                                        mosaic_same_day=False, 
                                                        roi=aoi_fc.first().geometry())
    
    collection_images = [(name, 
                          footprint, 
                          datetime.fromtimestamp(date/1000).strftime("%Y-%m-%d")) for 
                          name, footprint, date in zip(collection.aggregate_array('system:index').getInfo(), 
                                                                                              collection.aggregate_array('system:footprint').getInfo(), 
                                                                                              collection.aggregate_array('system:time_start').getInfo())]

    if len(collection_images) == 0:
        message = "No image found in this time range"
        if email_notif:
            email_notification(email_notif, message, success=False)
        return message

    sql = text('select * from image where name in :col and "user"=:user').bindparams(bindparam('col', expanding=True), bindparam('user'))
    matching_local = gpd.read_postgis(sql, con=engine, params={'col': [i[0] for i in collection_images], 'user': user}, crs=3857, geom_col="geometry")

    new_images = [n for n in collection_images if n[0] not in list(matching_local["name"])]

    if len(new_images) == 0:
        message = "No new image to download"
        if email_notif:
            email_notification(email_notif, message, success=False)
        return message
    
    new_images_gdf = gpd.GeoDataFrame(new_images, columns=['name', 'json_geom', 'date'], geometry=[Polygon(shape(f[1])) for f in new_images], crs=4326).to_crs(3857)
    new_images_gdf["user"] = user
    new_images_gdf["geometry"] = new_images_gdf.simplify(10)
    new_images_gdf["satellite"] = satellite_type
    new_images_gdf = new_images_gdf[["name", "date", "user", "satellite", "geometry"]]
    new_images_gdf.to_postgis(name='image', con=engine, if_exists='append')
    
    # RE-READ pour récupérer les FID assignés par pgsql
    sql = text('select * from image where name in :col and "user"=:user and path is null').bindparams(bindparam('col', expanding=True), bindparam('user'))
    new_images_gdf = gpd.read_postgis(sql, con=engine, params={'col': list(new_images_gdf['name']), 'user': user}, crs=3857, geom_col="geometry")

    try:
        collection = collection.filter(ee.Filter.inList('system:index', list(new_images_gdf["name"])))

        collection = classification.calculateIndicators(collection)
        collection = classification.classifyObjects(collection=collection, 
                                                    watermask_expression=watermask_expression,
                                                    activechannel_expression=activechannel_expression, 
                                                    vegetation_expression=vegetation_expression)
        
        output_dir = os.path.join(os.environ['GLOURBEE_DATASTORE'], 'all')
        os.makedirs(output_dir, exist_ok=True)

        with redirect_stdout(None):
            geemap.download_ee_image_collection(collection=collection, out_dir=output_dir, crs="EPSG:3857")

        with engine.connect() as con:
            sql = text('update image set path=concat(:dir, \'/\', "name", \'.tif\') where fid in :fids').bindparams(bindparam('dir'), bindparam('fids', expanding=True))
            con.execute(sql, parameters={'dir': output_dir, 'fids': list(new_images_gdf["fid"])})
            con.commit()

    except:
        with engine.connect() as con:
            sql = text('delete from image where fid in :fids').bindparams(bindparam('fids', expanding=True))
            con.execute(sql, parameters={'fids': list(new_images_gdf["fid"])})
            con.commit()

        message = 'Error processing images'
        if email_notif:
            email_notification(email_notif, message, success=False)
        return message

    message = f'{len(new_images_gdf)} images processed'
    if email_notif:
        email_notification(email_notif, message, success=True)
    return message


@app.task
def upload_archive(images: list[str], email: str):

    assert re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)
    for f in images:
        assert os.path.isfile(f)

    size_mo = sum([os.path.getsize(f) for f in images])/1000000
    
    assert size_mo < 20000

    with NamedTemporaryFile(suffix='.zip') as tmp:

        with ZipFile(tmp.name, 'w') as archive:
            for f in images:
                archive.write(f)

        call(['python', os.environ['FILESENDER_SCRIPT'], 
              "-b", os.environ['FILESENDER_BASE_URL'],
              "-u", os.environ['FILESENDER_USERNAME'],
              "-a", os.environ['FILESENDER_APIKEY'],
              "-f", os.environ["FILESENDER_FROM"],
              "-s", "GloUrbEE archive",
              "-m", "This archive contains the images you selected in GloUrbEE-UI",
              "-r", email,
              tmp.name])
        