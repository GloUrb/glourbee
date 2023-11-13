import ee


def calculateCloudScore(image, dgo_shape, scale=30):
    
    cloud_mask = image.unmask().select('CLOUDS').eq(0)
    
    cloudy_size = cloud_mask.reduceRegion(
        reducer = ee.Reducer.sum(),
        geometry = dgo_shape.geometry(),
        scale = scale
    ).getNumber('CLOUDS')
    
    full_size = cloud_mask.reduceRegion(
        reducer = ee.Reducer.count(),
        geometry = dgo_shape.geometry(),
        scale = scale
    ).getNumber('CLOUDS')
    
    cloud_score = cloudy_size.divide(full_size).multiply(100).round()

    return cloud_score


def calculateCoverage(image, dgo_shape, scale=30):
    # Calculate how much an image cover a DGO
    
    unmasked = image.unmask(1)
    
    total_pixels = dgo_shape.area(maxError=1, proj=image.projection())
    
    act_pixels = unmasked.reduceRegion(
        reducer = ee.Reducer.count(),
        geometry = dgo_shape.geometry(),
        scale = scale,
        maxPixels = 1e13
    ).getNumber('red')
    
    coverage_score = act_pixels.divide(total_pixels).multiply(100).round()

    return coverage_score


def calculateWaterMetrics(image, dgo, scale=30, simplify_tolerance=1.5):
    # Vectorisation des surfaces
    water = image.select('WATER').reduceToVectors(
        geometry = dgo.geometry(),
        scale = scale,
        eightConnected = True,
        maxPixels = 1e12,
        geometryType = 'polygon')
    
    # Séparer les surfaces en eau et les surfaces émergées
    vector_water = water.filter("label == 1")
    vector_dry = water.filter("label == 0")
    
    # Initialisation du dictionnaire des résultats
    results = dict()
    
    # Calculer l'aire des surfaces en eau
    results['WATER_AREA'] = image.select('WATER').reduceRegion(
        reducer = ee.Reducer.sum(),
        geometry = vector_water,
        scale = scale
    ).getNumber('WATER')
    
    # Simplifier les géométries
    geoms_water = vector_water.geometry().simplify(scale*simplify_tolerance)
    
    # Calucler les périmètres
    results['WATER_PERIMETER'] = geoms_water.perimeter(scale)
    
    # Calcul du mndwi moyen des surfaces en eau
    results['MEAN_WATER_MNDWI'] = image.select('MNDWI').reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = vector_water,
        scale = scale
        ).getNumber('MNDWI')
    
    # Calcul du mndwi moyen des surfaces émergées
    results['MEAN_DRY_MNDWI'] = image.select('MNDWI').reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = vector_dry,
        scale = scale
        ).getNumber('MNDWI')
    
    # Calcul du mndwi moyen de tout le DGO
    results['MEAN_MNDWI'] = image.select('MNDWI').reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = dgo.geometry(),
        scale = scale
        ).getNumber('MNDWI')
    
    return results



def calculateVegetationMetrics(image, dgo, scale=30, simplify_tolerance=1.5):
    # Vectorisation des surfaces
    vectors = image.select('VEGETATION').reduceToVectors(
        geometry = dgo.geometry(),
        scale = scale,
        eightConnected = True,
        maxPixels = 1e12,
        geometryType = 'polygon')
    
    # Séparer les surfaces végétation du reste
    vector_vegetation = vectors.filter("label == 1")
    
    # Initialisation du dictionnaire des résultats
    results = dict()

    # Calculer l'aire des surfaces végétation
    results['VEGETATION_AREA'] = image.select('VEGETATION').reduceRegion(
        reducer = ee.Reducer.sum(),
        geometry = vector_vegetation,
        scale = scale
    ).getNumber('VEGETATION')
    
    # Simplifier les géométries
    geom_vegetation = vector_vegetation.geometry().simplify(scale*simplify_tolerance)
    
    # Calucler les périmètres
    results['VEGETATION_PERIMETER'] = geom_vegetation.perimeter(scale)
    
    # Calcul du ndvi moyen des surfaces végétation
    results['MEAN_VEGETATION_NDVI'] = image.select('NDVI').reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = vector_vegetation,
        scale = scale
        ).getNumber('NDVI')
    
    # Calcul du mndwi moyen des surfaces végétation
    results['MEAN_VEGETATION_MNDWI'] = image.select('MNDWI').reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = vector_vegetation,
        scale = scale
        ).getNumber('MNDWI')
    
    # Calcul du ndvi moyen de tout le DGO
    results['MEAN_NDVI'] = image.select('NDVI').reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = dgo.geometry(),
        scale = scale
        ).getNumber('NDVI')
        
    return results


def calculateACMetrics(image, dgo, scale=30, simplify_tolerance=1.5):
    # Vectorisation des surfaces
    vectors = image.select('AC').reduceToVectors(
        geometry = dgo.geometry(),
        scale = scale,
        eightConnected = True,
        maxPixels = 1e12,
        geometryType = 'polygon')
    
    # Séparer les surfaces végétation du reste
    vector_ac = vectors.filter("label == 1")
    
    # Initialisation du dictionnaire des résultats
    results = dict()

    # Calculer l'aire des surfaces végétation
    results['AC_AREA'] = image.select('AC').reduceRegion(
        reducer = ee.Reducer.sum(),
        geometry = vector_ac,
        scale = scale
    ).getNumber('AC')
    
    # Calcul du ndvi moyen des surfaces végétation
    results['MEAN_AC_NDVI'] = image.select('NDVI').reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = vector_ac,
        scale = scale
        ).getNumber('NDVI')
    
    # Calcul du mndwi moyen des surfaces végétation
    results['MEAN_AC_MNDWI'] = image.select('MNDWI').reduceRegion(
        reducer = ee.Reducer.mean(),
        geometry = vector_ac,
        scale = scale
        ).getNumber('MNDWI')
        
    return results


def dgoMetrics(collection):
    def mapDGO(dgo):
        # Filtrer la collection d'images sur l'emprise du DGO traité
        dgo_images_collection = collection.filterBounds(dgo.geometry())

        # Définir une fonction qui ajoute les métriques d'une image à la liste des métriques du DGO
        def addMetrics(image, metrics_list):
            # Récupérer la Feature du DGO qui est stocké dans le premier élément de la liste
            dgo = ee.Feature(ee.List(metrics_list).get(0))
            
            # Calculer les métriques
            cloud_score = calculateCloudScore(image, dgo)
            coverage_score = calculateCoverage(image, dgo)
            water_metrics = calculateWaterMetrics(image, dgo)
            vegetation_metrics = calculateVegetationMetrics(image, dgo)
            ac_metrics = calculateACMetrics(image, dgo)
            
            # Créer un dictionnaire avec toutes les métriques
            image_metrics = dgo.set({
                                     'DATE': ee.Date(image.get('system:time_start')).format("YYYY-MM-dd"),
                                     'CLOUD_SCORE': cloud_score, 
                                     'COVERAGE_SCORE': coverage_score,
                                     **water_metrics,
                                     **vegetation_metrics,
                                     **ac_metrics
                                    })
            
            # Filtrer si le DGO est 100% couvert de nuages
            output_list = ee.Algorithms.If(ee.Number(cloud_score).gte(ee.Number(100)), ee.List(metrics_list), ee.List(metrics_list).add(image_metrics))
            
            # Ajouter ce dictionnaire à la liste des métriques
            return output_list

        # Stocker le DGO traité dans le premier élément de la liste
        first = ee.List([dgo])

        # Ajouter les métriques calculées sur chaque image à la liste
        metrics = dgo_images_collection.iterate(addMetrics, first)

        # Supprimer le DGO traité de la liste pour alléger le résultat
        metrics = ee.List(metrics).remove(dgo)

        # Renvoyer la Feature en ajoutant l'attribut metrics
        return dgo.set({'metrics': metrics})
    return mapDGO


def calculateDGOsMetrics(collection, dgos):
    # Ajouter les listes de métriques aux attributs des DGOs
    metrics = dgos.map(dgoMetrics(collection))

    # Dé-empiler les métriques stockées dans un attribut de la FeatureCollection
    unnested = ee.FeatureCollection(metrics.aggregate_array('metrics').flatten())

    # Retourner uniquement les métriques (pas la Feature complète)
    return unnested

