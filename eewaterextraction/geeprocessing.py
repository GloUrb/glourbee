import ee

from eewaterextraction.classification import calculateCloudScore


def selectDGOs(dgo_shp, dgo_list):
    # Extraire l'entité des DGO dans la liste
    filter = ee.Filter.inList('DGO_FID', dgo_list)
    selected_dgo = dgo_shp.filter(filter)
    
    return selected_dgo


def getLandsatCollection(start, end, cloud_filter):  
    # Récupération des images
    landsat_collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5','SR_B6','SR_B7','QA_PIXEL'])
        .map(lambda image: image.rename(['B1', 'B2', 'B3', 'B4','B5','B7','QA_PIXEL']))
        .merge(ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4','SR_B5','SR_B7','QA_PIXEL']))
        .map(lambda image: image.rename(['B1', 'B2', 'B3', 'B4','B5','B7','QA_PIXEL']))
        .merge(ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4','SR_B5','SR_B7','QA_PIXEL']))
        .map(lambda image: image.rename(['B1', 'B2', 'B3', 'B4','B5','B7','QA_PIXEL']))
        .merge(ee.ImageCollection('LANDSAT/LT04/C02/T1_L2').select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4','SR_B5','SR_B7','QA_PIXEL']))
        .map(lambda image: image.rename(['B1', 'B2', 'B3', 'B4','B5','B7','QA_PIXEL'])))
    
    # Filtrage des dates
    landsat_collection = landsat_collection.filterDate(start, end)
    
    # Filtrage du cloud cover
    landsat_collection = landsat_collection.filter(ee.Filter.lte('CLOUD_COVER', cloud_filter))
    
    return landsat_collection


def filterDGO(collection, unique_dgo, landsat_scale, cloud_filter = None):
    # Filtrage de la collection sur l'étendue du DGO
    filtered_collection = collection.filterBounds(unique_dgo.geometry()) 
    
    # Filtrage du cloud cover
    if cloud_filter:
        filtered_collection = filtered_collection.map(calculateCloudScore(unique_dgo, landsat_scale))
        filtered_collection = filtered_collection.filter(ee.Filter.lte('CLOUD_SCORE', cloud_filter))
    
    return filtered_collection