import ee
import tempfile
import os
import uuid
import pandas as pd
import geopandas as gpd
from urllib.request import urlretrieve
from time import sleep
from datetime import datetime


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

        self.gee_dir = f'projects/{self.ee_project_name}/assets/extraction_zones/{asset_uuid}'

        self.asset_uuid = asset_uuid
        if not self.asset_uuid:
            self.asset_uuid = uuid.uuid4().hex

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
                asset for asset in dir_content['assets'] if asset['type'] == 'TABLE']
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
                 local_file: str = './example_data/Lhasa_RC_DGO2km_updated.shp', 
                 ee_project_name: str = 'ee-glourb', 
                 asset_uuid: str = None,
                 fid_field: str = 'DGO_FID',
                 zone_type: str = 'DGOs'):
        
        super().__init__(ee_project_name, asset_uuid)

        self.child_metrics = []
        self.fid_field = fid_field

        # Vérifier que le fichier local existe
        self.local_file = local_file
        assert os.path.exists(
            self.local_file), f'Local file {self.local_file} does not exist.'
        
        # Vérifier que le champ FID existe
        gdf = gpd.read_file(self.local_file)
        assert self.fid_field in gdf.columns, f'FID field {self.fid_field} does not exist in the local file.'
        assert gdf[self.fid_field].dtype.kind in 'iu', f'FID field {self.fid_field} should be an integer.'
        
        # Récupérer le nombre d'entités
        gdf = gpd.read_file(self.local_file)
        self.len = len(gdf)

        # Récupérer le nom du fichier
        self.name = os.path.splitext(os.path.basename(self.local_file))[0]

        # Récupérer les infos sur le dossier GEE
        self.gee_dir = f'projects/{self.ee_project_name}/assets/extraction_zones/{self.asset_uuid}'
        self.update_gee_state()

    def upload_to_gee(self, simplify_tolerance: int = 15, silent: bool = False):
        """
        Upload the extraction zones to Earth Engine.

        Args:
            simplify_tolerance (int, optional): Tolerance for simplifying the geometries. Defaults to 15.
            silent (bool, optional): If True, do not print progress. Defaults to False.
        """

        assert simplify_tolerance >= 1, 'Simplify tolerance should be >= 1'

        # Ouvrir le fichier local
        gdf = gpd.read_file(self.local_file)
        gdf['geometry'] = gdf.simplify(simplify_tolerance)
        gdf.to_crs(4326, inplace=True)

        # splitted_gdf = np.array_split(gdf, self.len)

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

        self.parent_zones = parent_zones
        self.len = self.parent_zones.len

        self.name = f'{self.parent_zones.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

        self.gee_dir = f'{self.parent_zones.gee_dir}/{self.asset_uuid}'
        self.update_gee_state()


    def compute_zone_metrics(self, fid: int, metrics: ee.FeatureCollection, silent: bool = False):
        """
        Compute the metrics for a zone and upload them to Earth Engine.

        Args:
            fid (int): Feature ID of the zone.
            metrics (ee.FeatureCollection): Metrics to upload.
            silent (bool, optional): If True, do not print progress. Defaults to False.
        """

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

                # Nettoyer les champs et supprimer les géométries pour alléger la sortie
                df = pd.read_csv(temp_file, index_col=None, header=0)
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