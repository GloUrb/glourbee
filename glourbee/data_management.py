import ee
import geemap
from geetools import tools


def maskClouds(image):
    
    cloudShadowBitMask = (1 << 3)
    cloudsBitMask = (1 << 5)
    
    qa = image.select('qa_pixel')
    clouds = (qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(qa.bitwiseAnd(cloudsBitMask).eq(0))).rename('CLOUDS')
    
    return image.updateMask(clouds).addBands(clouds)


def getLandsatCollection(start=ee.Date('1980-01-01'), end=ee.Date('2100-01-01'), cloud_masking=True, cloud_filter=None, roi=None, mosaic_same_day=False):  
    '''
    Documentation
    '''
    
    # Définition des noms de bandes 
    bnd_names = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'qa_pixel']
    
    # Récupération des collections landsat
    l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5','SR_B6','SR_B7','QA_PIXEL'], bnd_names)
    l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2').select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4','SR_B5','SR_B7','QA_PIXEL'], bnd_names)
    l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2').select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4','SR_B5','SR_B7','QA_PIXEL'], bnd_names)
    l4 = ee.ImageCollection('LANDSAT/LT04/C02/T1_L2').select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4','SR_B5','SR_B7','QA_PIXEL'], bnd_names)
    
    # Merge de toutes les collections
    landsat_collection = ee.ImageCollection(l8.merge(l7).merge(l5).merge(l4)).filterDate(start, end)
        
    # Suppression des images avec trop de nuages
    if cloud_filter:
        landsat_collection = landsat_collection.filter(ee.Filter.lte('CLOUD_COVER', cloud_filter))
        
    # Filtrage de la région d'intérêt
    if roi:
        landsat_collection = landsat_collection.filterBounds(roi)
    
    # Masquage des nuages restants
    if cloud_masking:
        landsat_collection = landsat_collection.map(maskClouds)

    # Mosaiquage par jour de prise de vue pour réduire la taille de la collection
    if mosaic_same_day:
        landsat_collection = tools.imagecollection.mosaicSameDay(landsat_collection)
    
    return landsat_collection


def imageDownload(collection, landsat_id, roi, scale=90, output='./example_data/landsat_export.tif'):
    image = collection.filter(ee.Filter.eq('LANDSAT_PRODUCT_ID', landsat_id)).first()

    geemap.ee_export_image(
        image, filename=output, scale=scale, region=roi.geometry(), file_per_band=False
    )
    