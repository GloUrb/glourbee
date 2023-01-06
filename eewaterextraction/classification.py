import ee


def calculateMNDWI(image):
    # Calculer l'image de MNDWI
    output_img = image.normalizedDifference(['B2','B5']).rename('MNDWI')
    
    # Copier la propriété DATE_ACQUIRED
    output_img = output_img.copyProperties(
        source = image,
        properties = ['DATE_ACQUIRED']
    )
    
    return output_img


def extractWater(mndwi):
    # Seuillage du raster
    raster_water = mndwi.expression('MNDWI >  0.0', {'MNDWI': mndwi.select('MNDWI')}).rename('WATER')
    
    # Filtre modal pour retirer les pixels isolés
    raster_water = raster_water.focalMode(3)
    
    return raster_water


def calculateCloudScore(dgo_shape, landsat_scale):
    def mapImage(image):
        cloudShadowBitMask = (1 << 3)
        cloudsBitMask = (1 << 5)
        
        qa = image.select('QA_PIXEL')
        cloud_mask = (qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(qa.bitwiseAnd(cloudsBitMask).eq(0)))
        
        cloudy_size = cloud_mask.reduceRegion(
            reducer = ee.Reducer.sum(),
            geometry = dgo_shape.geometry(),
            scale = landsat_scale
        )
        
        full_size = cloud_mask.reduceRegion(
            reducer = ee.Reducer.count(),
            geometry = dgo_shape.geometry(),
            scale = landsat_scale
        )
        
        cloud_score = cloudy_size.getNumber('QA_PIXEL').divide(full_size.getNumber('QA_PIXEL')).multiply(100)

        return image.set({'CLOUD_SCORE': cloud_score})
    return mapImage