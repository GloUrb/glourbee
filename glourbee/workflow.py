import ee
import os
import uuid
import numpy as np
import pandas as pd
from urllib.request import urlretrieve
from urllib.error import HTTPError

import tempfile

from urllib.request import urlretrieve
from urllib.error import HTTPError

from glourbee import (
    classification,
    data_management,
    zones_indicators,
    zones_metrics
)

tempdir = tempfile.mkdtemp(prefix='glourbee_')

def startWorkflow(zones_asset: str,
                  ee_project_name: str = 'ee-glourb',
                  satellite_type: str = 'Landsat',
                  start: str = '1980-01-01',
                  end: str = '2030-12-31',
                  cloud_filter: int = 80,
                  cloud_masking: bool = True,
                  mosaic_same_day: bool = True,
                  split_size: int = None,
                  fid_field= 'ZONE_FID',
                  watermask_expression: str = 'MNDWI >  0.0',
                  activechannel_expression: str = 'MNDWI > -0.4 && NDVI < 0.2',
                  vegetation_expression: str = 'NDVI > 0.15'):
    """
    Execute the classical GloUrbEE workflow for processing satellite imagery data for given extraction zones

    This function processes satellite imagery data for the given extraction zones. It divides the polygons into subsets based on split_size, 
    collects satellite imagery data according to the specified parameters, calculates various indicators, classifies objects, 
    computes metrics, and exports the results as assets to the specified Earth Engine project.

    :param zones_asset (str): Asset ID or path of the FeatureCollection containing extraction zones.
    :param ee_project_name (str, optional): Earth Engine project name. Defaults to 'ee-glourb'.
    :param satellite_type (str, optional): Type of satellite imagery to use, 'Landsat' or 'Sentinel-2'. Defaults to 'Landsat'.
    :param start (str, optional): Start date for image collection (inclusive), formatted as 'YYYY-MM-DD'. Defaults to '1980-01-01'.
    :param end (str, optional): End date for image collection (inclusive), formatted as 'YYYY-MM-DD'. Defaults to '2030-12-31'.
    :param cloud_filter (int, optional): Maximum cloud coverage accepted for images, in percentage. Defaults to 80.
    :param cloud_masking (bool, optional): Whether to mask clouds on accepted images. Defaults to True.
    :param mosaic_same_day (bool, optional): Whether to merge all images taken on the same day. Defaults to True.
    :param split_size (int, optional): Size for splitting extraction zones into subsets for processing. Defaults to 50.
    :param fid_field (str, optional): Field name containing unique identifiers for extraction zones. Defaults to 'ZONE_FID'.
    :param watermask_expression (str, optional): Expression for water mask. Available bands are: BLUE, GREEN, RED, NIR, SWIR1, SWIR2, MNDWI, NDWI, NDVI. Defaults to 'MNDWI >  0.0'.
    :param activechannel_expression (str, optional): Expression for active channel mask. Available bands are: BLUE, GREEN, RED, NIR, SWIR1, SWIR2, MNDWI, NDWI, NDVI. Defaults to 'MNDWI > -0.4 && NDVI < 0.2'.
    :param vegetation_expression (str, optional): Expression for vegetation mask. Available bands are: BLUE, GREEN, RED, NIR, SWIR1, SWIR2, MNDWI, NDWI, NDVI. Defaults to 'NDVI > 0.15'.

    :returns workflow_id (str): Unique identifier for the executed workflow.
    """


    assert satellite_type in ['Landsat', 'Sentinel-2'], ('Satellite dataset not correctly defined. Set satellite_type either to "Landsat" or "Sentinel-2"')

    if split_size:
        print('Warning: split_size is deprecated and will be removed in future versions. All ZONEs are now processed in parallel.')

    zones_features = ee.FeatureCollection(zones_asset)

    zone_fids = zones_features.aggregate_array(fid_field).getInfo()
    workflow_id = uuid.uuid4().hex

    for i, sub in enumerate(zone_fids):
        i+=1
        zone_subset = zones_features.filter(ee.Filter.inList(fid_field, sub.tolist()))
        
        if satellite_type == 'Landsat':
            scale = 30
            # Get the landsat image collection for your ROI
            collection = data_management.getLandsatCollection(start=ee.Date(start), 
                                                              end=ee.Date(end), 
                                                              cloud_filter=cloud_filter, # Maximum cloud coverage accepted (%)
                                                              cloud_masking=cloud_masking, # Set to False if you don't want to mask the clouds on accepted images
                                                              mosaic_same_day=mosaic_same_day, # Set to False if you don't want to merge all images by day
                                                              roi=zone_subset.union(1)) 

        elif satellite_type == 'Sentinel-2':
            scale = 10
            # Get the Sentinel-2 image collection for your ROI
            collection = data_management.getSentinelCollection(start=ee.Date(start), 
                                                              end=ee.Date(end), 
                                                              cloud_filter=cloud_filter, # Maximum cloud coverage accepted (%)
                                                              cloud_masking=cloud_masking, # Set to False if you don't want to mask the clouds on accepted images
                                                              mosaic_same_day=mosaic_same_day, # Set to False if you don't want to merge all images by day
                                                              roi=zone_subset.union(1)) 

        # Calculate MNDWI, NDVI and NDWI
        collection = classification.calculateIndicators(collection)

        # Classify the objects using the indicators
        collection = classification.classifyObjects(collection=collection, 
                                                    watermask_expression=watermask_expression, 
                                                    activechannel_expression=activechannel_expression, 
                                                    vegetation_expression=vegetation_expression)

        # Metrics calculation
        metrics = zones_metrics.calculateZONEsMetrics(collection=collection, zones=zone_subset, scale=scale)

        # Create computation task
        assetName = f'{workflow_id}_{i}'
        assetId = f'projects/{ee_project_name}/assets/metrics/tmp/{assetName}'

        task = ee.batch.Export.table.toAsset(
            collection=metrics,
            description=f'ZONE {i}-{len(zone_fids)} metrics for run {workflow_id}',
            assetId=assetId
        )
        task.start()

        print(f'\rZONE {i}/{len(zone_fids)} metrics queued', end=" ")
    
    return workflow_id


def workflowState(run_id):
    ee_tasks = ee.data.getTaskList()
    tasks = [t for t in ee_tasks if f'run {run_id}' in t['description']]

    # Check all tasks
    completed = len([t for t in tasks if t['state'] == 'COMPLETED'])
    running = len([t for t in tasks if t['state'] == 'RUNNING'])
    pending = len([t for t in tasks if t['state'] == 'PENDING'])
    ready = len([t for t in tasks if t['state'] == 'READY'])
    failed = len([t for t in tasks if t['state'] == 'FAILED'])

    print(f'{completed} tasks completed.')
    print(f'{running} tasks running.')
    print(f'{pending} tasks pending.')
    print(f'{ready} tasks ready.')
    print(f'{failed} tasks failed.')

    return tasks


def cancelWorkflow(run_id):
    ee_tasks = ee.data.getTaskList()
    tasks = [t for t in ee_tasks if f'run {run_id}' in t['description']]

    task_ids = [t['id'] for t in tasks]

    for tid in task_ids:
        ee.data.cancelTask(tid)


def getResults(run_id, ee_project_name, output_csv, overwrite=False, remove_tmp=False):
    ee_tasks = ee.data.getTaskList()
    stacked_uris = [t['destination_uris'] for t in ee_tasks if f'run {run_id}' in t['description'] and t['state'] == 'COMPLETED']
    uris = [uri.split(f'{ee_project_name}/assets/')[1] for sublist in stacked_uris for uri in sublist]

    assets = [f'projects/{ee_project_name}/assets/{uri}' for uri in uris]
    temp_csv_list = [os.path.join(tempdir, f'{os.path.basename(a)}.tmp.csv') for a in assets]
    
    for assetName, path in zip(assets, temp_csv_list):
        if not os.path.exists(path) or overwrite:
            asset = ee.FeatureCollection(assetName)

            # Télécharger l'asset complet et le nettoyer localement
            urlretrieve(asset.getDownloadUrl(), path)
            df = pd.read_csv(path, index_col=None, header=0)
            df = df.drop(['system:index', '.geo'], axis=1)
            df.to_csv(path)
        else:
            continue

    output_dfs = []
    for filename in temp_csv_list:
        df = pd.read_csv(filename, index_col=None, header=0)
        output_dfs.append(df)

        if remove_tmp:
            os.remove(filename)

    df = pd.concat(output_dfs, axis=0, ignore_index=True)
    df.to_csv(output_csv)


def cleanAssets(run_id, ee_project_name):
    ee_tasks = ee.data.getTaskList()
    stacked_uris = [t['destination_uris'] for t in ee_tasks if f'run {run_id}' in t['description'] and t['state'] == 'COMPLETED']
    uris = [uri.split(f'{ee_project_name}/assets/')[1] for sublist in stacked_uris for uri in sublist]

    assets_list = [f'projects/{ee_project_name}/assets/{uri}' for uri in uris]
    for asset in assets_list:
        ee.data.deleteAsset(asset)


def indicatorsWorkflow(zones_asset, output_csv):
    metrics = zones_indicators.calculateGSWindicators(zones_asset)
    
    temp_metrics = os.path.join(tempdir, 'gsw_metrics_output.csv')
    urlretrieve(metrics.getDownloadUrl(), temp_metrics)

    df = pd.read_csv(temp_metrics)
    df.drop(['system:index', '.geo'], axis=1, inplace=True)
    df.to_csv(output_csv)
