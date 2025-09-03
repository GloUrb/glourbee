import os
import ee
import geemap
import geopandas as gpd
import json

from sqlalchemy import text, create_engine
from celery import Celery
from time import sleep

app = Celery('glourbee-worker', 
             broker=os.environ['GLOURBEE_BROKER_URL'],
             backend=os.environ['GLOURBEE_BROKER_URL'])

engine = create_engine(os.environ['GLOURBEE_DB_URI'])


@app.task
def gee_process(aoi_fid: int,
                date_range: tuple[str, str], 
                cloud_filter: int = 80, 
                cloud_masking: bool = True, 
                satellite_type: str = "Landsat", 
                watermask_expression: str = "MNDWI >  0.0", 
                activechannel_expression: str = "NDWI > -0.4 && NDVI < 0.2", 
                vegetation_expression: str = "NDVI > 0.15"):
    
    assert satellite_type in ['Landsat', 'Sentinel']

    with open('/app/earthengine-key.json') as f:
        ee_json_key = json.load(f)
    credentials = ee.ServiceAccountCredentials(email=ee_json_key['client_email'], key_data=json.dumps(ee_json_key))
    ee.Initialize(credentials)

    from glourbee import data_management, classification

    aoi_gdf = gpd.read_postgis(text("select * from aoi where fid=:fid"), con=engine, params={'fid': aoi_fid}, crs=3857, geom_col="geometry")
    # images_gdf = gpd.read_postgis()

    aoi_fc = geemap.gdf_to_ee(aoi_gdf)

    if satellite_type == "Landsat":
        collection = data_management.getLandsatCollection(start=ee.Date(date_range[0]), 
                                                        end=ee.Date(date_range[1]), 
                                                        cloud_filter=cloud_filter,
                                                        cloud_masking=cloud_masking,
                                                        mosaic_same_day=False, 
                                                        roi=aoi_fc.first().geometry())
    elif satellite_type == "Sentinel":
        collection = data_management.getSentinelCollection(start=ee.Date(date_range[0]), 
                                                        end=ee.Date(date_range[1]), 
                                                        cloud_filter=cloud_filter,
                                                        cloud_masking=cloud_masking,
                                                        mosaic_same_day=False, 
                                                        roi=aoi_fc.first().geometry())
    
    collection_images = [f'{name}.tif' for name in collection.aggregate_array('system:index').getInfo()]


    collection = classification.calculateIndicators(collection)
    collection = classification.classifyObjects(collection=collection, 
                                                watermask_expression=watermask_expression, 
                                                activechannel_expression=activechannel_expression, 
                                                vegetation_expression=vegetation_expression)
    
    output_dir = os.path.join(os.environ['GLOURBEE_DATASTORE'], 'all')
    os.makedirs(output_dir, exist_ok=True)

    geemap.download_ee_image_collection(collection=collection, out_dir=output_dir)

    return
