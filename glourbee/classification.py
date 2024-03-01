import ee

######
# Indicators


def calculateMNDWI(image):
    # Calculer l'image de MNDWI
    output_img = image.normalizedDifference(['green', 'swir1']).rename('MNDWI')

    return image.addBands(output_img)


def calculateNDVI(image):
    # Calculer l'image de MNDWI
    output_img = image.normalizedDifference(['nir', 'red']).rename('NDVI')

    return image.addBands(output_img)


def calculateNDWI(image):
    # Calculer l'image de MNDWI
    output_img = image.normalizedDifference(['green', 'nir']).rename('NDWI')

    return image.addBands(output_img)


def calculateIndicators(collection):
    '''
    Documentation
    '''

    collection = collection.map(calculateMNDWI).map(
        calculateNDVI).map(calculateNDWI)

    return collection


######
# Thresholds to classify objects

def extractWater(watermask_expression: str = 'MNDWI >  0.0'):
    def mapImage(image):
        # Seuillage du raster
        output_img = image.expression(watermask_expression,
                                      {'BLUE': image.select('blue'),
                                       'GREEN': image.select('green'),
                                       'RED': image.select('red'),
                                       'NIR': image.select('nir'),
                                       'SWIR1': image.select('swir1'),
                                       'SWIR2': image.select('swir2'),
                                       'MNDWI': image.select('MNDWI'),
                                       'NDWI': image.select('NDWI'),
                                       'NDVI': image.select('NDVI')}).rename('WATER')

        # Filtre modal pour retirer les pixels isolés
        output_img = output_img.focalMode(3)

        # ## Meilleure option : tamisage. Je ne suis pas certain que ça fonctionne a 100% pour le moment.
        # # Labellisation
        # object_id = output_img.connectedComponents(ee.Kernel.square(1), maxSize=128)

        # # Mesurer la taille des patch en pixels : résultat dépendant de l'échelle ?
        # object_size = object_id.select('labels').connectedPixelCount(maxSize=128, eightConnected=True)

        # # Convertir les taille en surfaces m2
        # pixel_area = ee.Image.pixelArea()
        # object_area = object_size.multiply(pixel_area)

        # # Mettre à jour l'image en sortie
        # output_img = output_img.where(object_area.lt(1800), ee.Number(0))

        # Masquer ce qui n'est pas classé
        output_img = output_img.selfMask()

        return image.addBands(output_img)
    return mapImage


def extractVegetation(vegetation_expression: str = 'NDVI > 0.15'):
    def mapImage(image):
        # Seuillage du raster
        output_img = image.expression(vegetation_expression, {'BLUE': image.select('blue'),
                                                              'GREEN': image.select('green'),
                                                              'RED': image.select('red'),
                                                              'NIR': image.select('nir'),
                                                              'SWIR1': image.select('swir1'),
                                                              'SWIR2': image.select('swir2'),
                                                              'MNDWI': image.select('MNDWI'),
                                                              'NDWI': image.select('NDWI'),
                                                              'NDVI': image.select('NDVI')}).rename('VEGETATION')

        # Filtre modal pour retirer les pixels isolés
        output_img = output_img.focalMode(3)

        # Masquer ce qui n'est pas classé
        mask = (output_img.eq(1))
        output_img = output_img.updateMask(mask)

        return image.addBands(output_img)
    return mapImage


def extractActiveChannel(activechannel_expression: str = 'MNDWI > -0.4 && NDVI < 0.2'):
    def mapImage(image):
        # Seuillage du raster
        output_img = image.expression(activechannel_expression,
                                      {'BLUE': image.select('blue'),
                                       'GREEN': image.select('green'),
                                       'RED': image.select('red'),
                                       'NIR': image.select('nir'),
                                       'SWIR1': image.select('swir1'),
                                       'SWIR2': image.select('swir2'),
                                       'MNDWI': image.select('MNDWI'),
                                       'NDWI': image.select('NDWI'),
                                       'NDVI': image.select('NDVI')}
                                      ).rename('AC')

        # Filtre modal pour retirer les pixels isolés
        output_img = output_img.focalMode(3)

        # Masquer ce qui n'est pas classé
        mask = (output_img.eq(1))
        output_img = output_img.updateMask(mask)

        return image.addBands(output_img)
    return mapImage


def classifyObjects(collection,
                    watermask_expression: str = 'MNDWI >  0.0',
                    activechannel_expression: str = 'MNDWI > -0.4 && NDVI < 0.2',
                    vegetation_expression: str = 'NDVI > 0.15'):

    collection = collection.map(extractWater(watermask_expression)).map(extractVegetation(
        vegetation_expression)).map(extractActiveChannel(activechannel_expression))

    return collection
