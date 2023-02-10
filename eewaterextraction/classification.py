import ee

######
## Indicators

def calculateMNDWI(image):
    # Calculer l'image de MNDWI
    output_img = image.normalizedDifference(['green','swir1']).rename('MNDWI')
    
    return image.addBands(output_img)


def calculateNDVI(image):
    # Calculer l'image de MNDWI
    output_img = image.normalizedDifference(['nir','red']).rename('NDVI')
    
    return image.addBands(output_img)


def calculateNDWI(image):
    # Calculer l'image de MNDWI
    output_img = image.normalizedDifference(['green','nir']).rename('NDWI')
    
    return image.addBands(output_img)


def calculateIndicators(collection):
    '''
    Documentation
    '''
    
    collection = collection.map(calculateMNDWI).map(calculateNDVI).map(calculateNDWI)
    
    return collection


######
## Thresholds to classify objects

def extractWater(image):
    # Seuillage du raster
    output_img = image.expression('MNDWI >  0.0', {'MNDWI': image.select('MNDWI')}).rename('WATER')
    
    # Filtre modal pour retirer les pixels isolés
    output_img = output_img.focalMode(3)
    
    # Masquer ce qui n'est pas classé
    mask = (output_img.eq(1))
    output_img = output_img.updateMask(mask)
    
    return image.addBands(output_img)


def extractVegetation(image):
    # Seuillage du raster
    output_img = image.expression('NDVI > 0.15', {'NDVI': image.select('NDVI')}).rename('VEGETATION')
    
    # Filtre modal pour retirer les pixels isolés
    output_img = output_img.focalMode(3)
    
    # Masquer ce qui n'est pas classé
    mask = (output_img.eq(1))
    output_img = output_img.updateMask(mask)
    
    return image.addBands(output_img)


def extractActiveChannel(image):
    # Seuillage du raster
    output_img = image.expression('MNDWI > -0.4 && NDVI < 0.2', 
                                                         {'MNDWI': image.select('MNDWI'),
                                                          'NDVI': image.select('NDVI')}
                                                         ).rename('AC')
    
    # Filtre modal pour retirer les pixels isolés
    output_img = output_img.focalMode(3)
    
    # Masquer ce qui n'est pas classé
    mask = (output_img.eq(1))
    output_img = output_img.updateMask(mask)
    
    return image.addBands(output_img)


def classifyObjects(collection):
    
    collection = collection.map(extractWater).map(extractVegetation).map(extractActiveChannel)

    return collection
