import ee
import pandas as pd

def getGlourbeeExtractionZones(ee_project_name: str='ee-glourb'):

    extraction_zones = []

    root_dir = f'projects/{ee_project_name}/assets/extraction_zones'
    root_content = ee.data.listAssets({'parent': root_dir})
    root_names = [asset['name'] for asset in root_content['assets']]

    for asset in root_names:
        asset_content = ee.data.listAssets({'parent': asset})
        asset_names = [asset['name'] for asset in asset_content['assets']]

        if not f'{asset}/config' in asset_names:
            continue

        config = ee.FeatureCollection(f'{asset}/config').getInfo()['features'][0]['properties']

        metrics_names = [asset['name'] for asset in asset_content['assets'] if asset['type'] == 'FOLDER']
        config['metrics_ds'] = len(metrics_names)
        config['asset_uuid'] = asset.split('/')[-1]

        extraction_zones.append(config)

    return pd.DataFrame(extraction_zones)


def getGlourbeeMetrics(ee_project_name: str='ee-glourb', zones_uuid: str=None):
    assert zones_uuid, 'Please provide an extraction zones uuid'

    metrics_ds = []

    root_dir = f'projects/{ee_project_name}/assets/extraction_zones/{zones_uuid}'
    root_content = ee.data.listAssets({'parent': root_dir})
    metrics_names = [asset['name'] for asset in root_content['assets'] if asset['type'] == 'FOLDER']

    for asset in metrics_names:
        asset_content = ee.data.listAssets({'parent': asset})
        asset_names = [asset['name'] for asset in asset_content['assets']]

        if not f'{asset}/config' in asset_names:
            continue

        config = ee.FeatureCollection(f'{asset}/config').getInfo()['features'][0]['properties']
        config['asset_uuid'] = asset.split('/')[-1]

        metrics_ds.append(config)

    return pd.DataFrame(metrics_ds)