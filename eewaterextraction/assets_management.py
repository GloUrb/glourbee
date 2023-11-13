import ee
import geemap
import time
import uuid
from urllib.request import urlretrieve


def uploadAsset(collection, description, assetId):
    # Créer la tache d'export
    task = ee.batch.Export.table.toAsset(
        collection=collection,
        description=description,
        assetId=assetId
    )

    # Démarrer la tache d'export
    start = time.time()
    task.start()

    # Surveiller la tache d'export
    while task.active():
        print(f'\rUploading asset... ({time.time() - start}s elapsed)', end=" ")
        time.sleep(5)
    print(f'\rEnd of asset upload ({time.time() - start}s elapsed). You can reload your asset with this assetId: {assetId}')

    # Vérifier que la tache d'export s'est terminée correctement
    if task.status()['state'] == 'COMPLETED':
        return True
    else:
        print('{}'.format(task.status()))
        return False #TODO: replace by raise error
    

def uploadDGOs(dgo_shapefile_path, ee_project_name='ee-glourb'):
    # Charger les DGOs dans EarthEngine
    dgo_shp = geemap.shp_to_ee(dgo_shapefile_path)

    # Uploader l'asset
    assetId = f'projects/{ee_project_name}/assets/dgos_{uuid.uuid4().hex}'
    if uploadAsset(dgo_shp, 'DGOs uploaded from ee-water-extraction notebook', assetId):
        # Renvoyer l'asset exporté et son id
        return(assetId, ee.FeatureCollection(assetId))
    else:
        return #TODO: replace by raise error


def downloadMetrics(metrics, output_file, ee_project_name='ee-glourb'):
    # Calculer l'asset
    assetId = f'projects/{ee_project_name}/assets/metrics_{uuid.uuid4().hex}'
    if not uploadAsset(metrics, 'Metrics uploaded from ee-water-extraction notebook', assetId):
        return #TODO: replace by raise error
    else:
        # Recharger l'asset
        asset = ee.FeatureCollection(assetId)

        # Nettoyer les champs et supprimer les géométries pour alléger la sortie
        cleaned = asset.select(propertySelectors=[
                                    'DATE',
                                    'AC_AREA',
                                    'CLOUD_SCORE',
                                    'COVERAGE_SCORE',
                                    'DATE_ACQUIRED',
                                    'DGO_FID',
                                    'MEAN_AC_MNDWI',
                                    'MEAN_AC_NDVI',
                                    'MEAN_MNDWI',
                                    'MEAN_NDVI',
                                    'MEAN_VEGETATION_MNDWI',
                                    'MEAN_VEGETATION_NDVI',
                                    'MEAN_WATER_MNDWI',
                                    'VEGETATION_AREA',
                                    'VEGETATION_PERIMETER',
                                    'WATER_AREA',
                                    'WATER_PERIMETER'],
                                retainGeometry=False)

        # Télécharger le csv
        urlretrieve(cleaned.getDownloadURL(), output_file)