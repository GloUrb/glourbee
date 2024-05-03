import ee
import tempfile
import os
import uuid
import json
import ee.batch
import pandas as pd
import geopandas as gpd

from urllib.request import urlretrieve
from time import sleep
from datetime import datetime
from shapely.geometry import shape


class GlourbEEDataset:
    """
    Class for managing extraction zones in Earth Engine.
    """

    def __init__(self,
                 ee_project_name: str = 'ee-glourb',
                 asset_uuid: str = None):
        """
        Initialize the ExtractionZones object.
        """

        self.ee_project_name = ee_project_name
        self.gee_assets = []
        self.config = None

        self.gee_dir = f'projects/{self.ee_project_name}/assets/extraction_zones/{asset_uuid}'

        self.asset_uuid = asset_uuid
        if not asset_uuid:
            self.asset_uuid = uuid.uuid4().hex
        else:
            # Vérifier si une config existe lorsqu'un asset_uuid est fourni
            try:              
                dir_content = ee.data.listAssets({'parent': self.gee_dir})
                config_asset = f'{self.gee_dir}/config'
                if config_asset in [asset['name'] for asset in dir_content['assets']]:
                    self.config = ee.FeatureCollection(config_asset).getInfo()
            except:
                print(f'Asset {self.gee_dir} config not available.')
                self.config = None


    def update_gee_state(self):
        """
        Update the state of the asset in Earth Engine.
        """

        # Check assets
        root_dir = os.path.dirname(self.gee_dir)
        root_content = ee.data.listAssets({'parent': root_dir})
        root_names = [asset['name'] for asset in root_content['assets']]

        if not self.gee_dir in root_names:
            ee.data.createAsset({'type': 'Folder'}, self.gee_dir)
            self.gee_assets = []
            self.child_metrics = []
        else:
            dir_content = ee.data.listAssets({'parent': self.gee_dir})
            self.gee_assets = [
                asset for asset in dir_content['assets'] if asset['type'] == 'TABLE' and '/config' not in asset['name']]
            self.child_metrics = [
                asset for asset in dir_content['assets'] if asset['type'] == 'FOLDER']

        self.gee_state = 'none'

        if len(self.gee_assets) > 0:
            self.gee_state = f'partial ({len(self.gee_assets)}/{self.len})'

        if len(self.gee_assets) == self.len:
            self.gee_state = 'complete'

        # Check linked tasks
        ee_tasks = ee.data.listOperations()
        self.linked_tasks = [
            t for t in ee_tasks if f'{self.asset_uuid}' in t['metadata']['description'] and t['metadata']['state'] != 'COMPLETED']

    def wait_for_tasks(self, silent: bool = False):
        tasks = self.linked_tasks

        running_tasks = [t for t in tasks if t['metadata']['state'] in [
            'RUNNING', 'SUBMITTED', 'PENDING']]
        while len(running_tasks) > 0:
            if not silent:
                print(f'\rwaiting for {len(running_tasks)} tasks to finish', end=" ")
            
            sleep(10)
            self.update_gee_state()
            tasks = self.linked_tasks
            running_tasks = [
                t for t in tasks if t['metadata']['state'] in ['RUNNING', 'SUBMITTED', 'PENDING']]
            

    def cancel_linked_tasks(self, silent: bool = False):
        """
        Cancel the linked computation, upload or export running tasks.
        """
        self.update_gee_state()

        for i, task in enumerate(self.linked_tasks):
            ee.data.cancelOperation(task['name'])

            if not silent:
                print(
                    f'\rTask {i+1}/{len(self.linked_tasks)} cancelled', end=" ")

    def delete(self):
        """
        Delete the assets and all the assets from Earth Engine.
        """

        child_assets = ee.data.listAssets({'parent': self.gee_dir})['assets']

        if len(child_assets) > 0:
            for child in child_assets:
                if child['type'] in ['FOLDER','IMAGE_COLLECTION']:
                    
                    subchild_assets = ee.data.listAssets({'parent': child['name']})['assets']

                    if len(subchild_assets) > 0:
                        for subchild in subchild_assets:
                            ee.data.deleteAsset(subchild['name'])
                    
                ee.data.deleteAsset(child['name'])

        ee.data.deleteAsset(self.gee_dir)


class ExtractionZones(GlourbEEDataset):
    def __init__(self, 
                 local_file: str,
                 ee_project_name: str = 'ee-glourb', 
                 asset_uuid: str = None,
                 fid_field: str = 'DGO_FID',
                 zone_type: str = 'DGOs',
                 descritpion: str = None,
                 author: str = None):
        
        super().__init__(ee_project_name, asset_uuid)

        self.child_metrics = []

        # Vérifier que le fichier local existe ou que l'asset est déjà sur GEE
        self.local_file = local_file
        assert os.path.exists(self.local_file) or self.config, f'Local file must exist or asset should be already uploaded to GEE project.'
        
        # Récupérer les paramètres
        if self.config:
            print('Asset already exists in GEE project. Loading config.')
            self.len = self.config['features'][0]['properties']['len']
            self.name = self.config['features'][0]['properties']['name']
            self.fid_field = self.config['features'][0]['properties']['fid_field']
            self.type = self.config['features'][0]['properties']['type']
            self.descritpion = self.config['features'][0]['properties']['descritpion']
            self.zones_author = self.config['features'][0]['properties']['zones_author']
        else:
            # Vérifier que le champ FID existe
            gdf = gpd.read_file(self.local_file)
            self.fid_field = fid_field
            assert self.fid_field in gdf.columns, f'FID field {self.fid_field} does not exist in the local file.'
            assert gdf[self.fid_field].dtype.kind in 'iu', f'FID field {self.fid_field} should be an integer.'

            self.name = os.path.splitext(os.path.basename(self.local_file))[0]
            self.len = len(gdf)
            self.type = zone_type
            self.descritpion = descritpion
            self.zones_author = author

        # Récupérer les infos sur le dossier GEE
        self.gee_dir = f'projects/{self.ee_project_name}/assets/extraction_zones/{self.asset_uuid}'
        self.update_gee_state()

    def upload_to_gee(self, simplify_tolerance: int = 15, silent: bool = False, overwrite: bool = False):
        """
        Upload the extraction zones to Earth Engine.

        Args:
            simplify_tolerance (int, optional): Tolerance for simplifying the geometries. Defaults to 15.
            silent (bool, optional): If True, do not print progress. Defaults to False.
        """

        assert simplify_tolerance >= 1, 'Simplify tolerance should be >= 1'
        assert not self.config or overwrite == True, 'Config already exists in GEE project. Set overwrite to True to overwrite extraction zones and metrics associated.'

        if overwrite:
            self.delete()
            self.update_gee_state()

        # Ouvrir le fichier local
        gdf = gpd.read_file(self.local_file)
        gdf['geometry'] = gdf.simplify(simplify_tolerance)
        gdf.to_crs(4326, inplace=True)

        extent = gdf.dissolve()

        # Mise à jour de la config
        self.config = {
            'type': 'FeatureCollection',
            'columns': {
                'fid_field': 'String',
                'len': 'Integer',
                'name': 'String',
                'type': 'String',
                'descritpion': 'String',
                'zones_author': 'String', 
                },
            'features': [
                {
                    'type': 'Feature',
                    'id': '0',
                    'properties': {
                        'fid_field': self.fid_field,
                        'len': self.len,
                        'name': self.name,
                        'type': self.type,
                        'descritpion': self.descritpion,
                        'zones_author': self.zones_author,
                    },
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [list(extent['geometry'][0].exterior.coords)]
                    },
                }
            ]
        }
        task = ee.batch.Export.table.toAsset(
            collection=ee.FeatureCollection(self.config),
            description=f'upload {self.asset_uuid} config',
            assetId=f'{self.gee_dir}/config'
        )
        task.start()

        # Boucler sur les entités
        for row in gdf.iterfeatures():
            fc = ee.FeatureCollection([ee.Feature(row)])
            fid = row['properties'][self.fid_field]

            assetId = f'{self.gee_dir}/{self.name}_{fid:04}'

            # Créer la tache d'export
            task = ee.batch.Export.table.toAsset(
                collection=fc,
                description=f'upload {self.asset_uuid} fid {fid:04}',
                assetId=assetId
            )
            task.start()

            if not silent:
                print(f'\rUpload zone {fid:04} started', end=" ")
            
        self.update_gee_state()
        

class MetricsDataset(GlourbEEDataset):
    def __init__(self, 
                 ee_project_name: str = 'ee-glourb', 
                 asset_uuid: str = None,
                 parent_zones: ExtractionZones = None):
        super().__init__(ee_project_name, asset_uuid)

        assert parent_zones, 'Parent extraction zones should be provided.'

        self.parent_zones = parent_zones
        self.len = self.parent_zones.len

        self.name = f'{self.parent_zones.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

        self.gee_dir = f'{self.parent_zones.gee_dir}/{self.asset_uuid}'
        self.update_gee_state()


    def compute_zone_metrics(self, fid: int, metrics: ee.FeatureCollection, params: dict, silent: bool = False):
        """
        Compute the metrics for a zone and upload them to Earth Engine.

        Args:
            fid (int): Feature ID of the zone.
            metrics (ee.FeatureCollection): Metrics to upload.
            silent (bool, optional): If True, do not print progress. Defaults to False.
        """

        # Create config if not exists
        if not self.config:
            self.config = self.parent_zones.config
            self.config['columns'].update({
                'satellite_type': 'String',
                'start': 'String',
                'end': 'String',
                'cloud_filter': 'Float',
                'cloud_masking': 'Boolean',
                'mosaic_same_day': 'Boolean',
                'watermask_expression': 'String',
                'activechannel_expression': 'String',
                'vegetation_expression': 'String',
               })
            self.config['features'][0]['properties'].update({
                'satellite_type': params['satellite_type'],
                'start': params['start'],
                'end': params['end'],
                'cloud_filter': params['cloud_filter'],
                'cloud_masking': params['cloud_masking'],
                'mosaic_same_day': params['mosaic_same_day'],
                'watermask_expression': params['watermask_expression'],
                'activechannel_expression': params['activechannel_expression'],
                'vegetation_expression': params['vegetation_expression'],
            })

            task = ee.batch.Export.table.toAsset(
                collection=ee.FeatureCollection(self.config),
                description=f'compute {self.asset_uuid} config',
                assetId=f'{self.gee_dir}/config'
            )
            task.start()

        assetId = f'{self.gee_dir}/{self.name}_{fid:04}'

        # Créer la tache d'export
        task = ee.batch.Export.table.toAsset(
            collection=metrics,
            description=f'compute {self.asset_uuid} fid {fid:04}',
            assetId=assetId
        )
        task.start()

        if not silent:
            print(f'\rCompute metrics for zone {fid:04} started', end=" ")

        self.update_gee_state()


    def download(self, output_file: str = './example_data/output.csv', overwrite: bool = False, silent: bool = False):
        """
        Download the assets from Earth Engine.

        Args:
            output_file (str): Path to the output file.
        """

        self.update_gee_state()

        output_ext = os.path.splitext(output_file)[1]
        assert output_ext in ['.csv'], 'Output file should be a .csv file.'

        assert len(self.gee_assets) > 0, 'No assets to download.'

        tempdir = tempfile.TemporaryDirectory()
        for i, assetData in enumerate(self.gee_assets):
            temp_file = os.path.join(
                tempdir.name, f'{os.path.basename(assetData["name"])}.csv')

            if os.path.exists(temp_file) and not overwrite:
                continue
            else:
                asset = ee.FeatureCollection(assetData['name'])

                if not silent:
                    print(
                        f'\rDownloading {os.path.basename(assetData["name"])} ({i+1}/{len(self.gee_assets)})', end=" ")

                # Télécharger l'asset
                urlretrieve(asset.getDownloadUrl(), temp_file)

                # Toilettage pour compatilité avec riviewlet (https://github.com/lvaudor/riviewlet)
                df = pd.read_csv(temp_file, index_col=None, header=0)
                df['ID'] = df[self.parent_zones.fid_field]
                df['geometry'] = df.apply(lambda row: shape(json.loads(row['.geo'])).centroid, axis=1)
                df = df.drop(['system:index', '.geo'], axis=1)
                df.to_csv(temp_file)

        # Concaténer les fichiers temporaires
        if not silent:
            print(f'\rConcatenating downloaded files', end=" ")

        output_dfs = []
        for filename in os.listdir(tempdir.name):
            df = pd.read_csv(os.path.join(
                tempdir.name, filename), index_col=None, header=0)
            output_dfs.append(df)

        df = pd.concat(output_dfs, axis=0, ignore_index=True)
        df.to_csv(output_file)

def uploadDGOs(dgo_shapefile_path, simplify_tolerance=15, ee_project_name='ee-glourb'):
    raise DeprecationWarning('This function is deprecated. Use ExtractionZones.upload_to_gee() method instead.')

def downloadMetrics(metrics, output_file, ee_project_name='ee-glourb'):
    raise DeprecationWarning('This function is deprecated. Use MetricsDataset.download() method instead.')