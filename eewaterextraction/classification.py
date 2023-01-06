
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