import ee


def calculateCloudScore(image, zone_shape, scale):
    
    cloud_mask = image.unmask().select('CLOUDS').eq(0)
    
    cloudy_size = cloud_mask.reduceRegion(
        reducer = ee.Reducer.sum(),
        geometry = zone_shape.geometry(),
        scale = scale
    ).getNumber('CLOUDS')
    
    full_size = cloud_mask.reduceRegion(
        reducer = ee.Reducer.count(),
        geometry = zone_shape.geometry(),
        scale = scale
    ).getNumber('CLOUDS')
    
    cloud_score = cloudy_size.divide(full_size).multiply(100).round()

    return cloud_score


def calculateCoverage(image, zone_shape, scale):
    # Calculate how much an image cover a ZONE
    
    unmasked = image.unmask(1)
    
    total_pixels = zone_shape.area(maxError=1, proj=image.select('blue').projection())
    
    act_pixels = unmasked.reduceRegion(
        reducer = ee.Reducer.count(),
        geometry = zone_shape.geometry(),
        scale = scale,
        maxPixels = 1e13
    ).getNumber('red')
    
    coverage_score = act_pixels.divide(total_pixels).multiply(100).round()

    return coverage_score


def calculateWaterMetrics(image, zone, scale, simplify_tolerance=1.5):
    # Vectorisation des surfaces
    water = image.select('WATER').reduceToVectors(
        geometry = zone.geometry(),
        scale = scale,
        eightConnected = True,
        maxPixels = 1e12,
        geometryType = 'polygon')
    
    # Séparer les surfaces en eau et les surfaces émergées
    vector_water = water.filter("label == 1")
    # vector_dry = water.filter("label == 0")
    
    # Simplifier les géométries pour le périmètre
    geoms_water = vector_water.geometry().simplify(scale*simplify_tolerance)

    # Calculer les percentiles de taille de polygones
    water_percentiles = vector_water.aggregate_array('count').reduce(ee.Reducer.percentile(
        percentiles=list(range(0,110,10)),
        outputNames=[f'WATER_POLYGONS_p{pc}' for pc in range(0,110,10)]
    ))

    # Initialisation du dictionnaire des résultats
    results = ee.Dictionary(water_percentiles).combine(ee.Dictionary({
        # Calculer le nombre de polygones d'eau
        'WATER_POLYGONS': vector_water.size(),

        # Calculer l'aire des surfaces en eau
        'WATER_AREA': image.select('WATER').reduceRegion(
                reducer = ee.Reducer.sum(),
                geometry = vector_water,
                scale = scale
            ).getNumber('WATER'),

        # Calculer les périmètres
        'WATER_PERIMETER': geoms_water.perimeter(scale),

        # Calcul du mndwi moyen des surfaces en eau
        'MEAN_WATER_MNDWI': image.select('MNDWI').reduceRegion(
                reducer = ee.Reducer.mean(),
                geometry = vector_water,
                scale = scale
            ).getNumber('MNDWI'),

        # # Calcul du mndwi moyen des surfaces émergées
        # 'MEAN_DRY_MNDWI': image.select('MNDWI').reduceRegion(
        #         reducer = ee.Reducer.mean(),
        #         geometry = vector_dry,
        #         scale = scale
        #     ).getNumber('MNDWI'),

        # Calcul du mndwi moyen de tout le ZONE
        'MEAN_MNDWI': image.select('MNDWI').reduceRegion(
                reducer = ee.Reducer.mean(),
                geometry = zone.geometry(),
                scale = scale
            ).getNumber('MNDWI'),

        'MEAN_BSI': image.select('BSI').reduceRegion(
                reducer = ee.Reducer.mean(),
                geometry = zone.geometry(),
                scale = scale
            ).getNumber('BSI'),
    }))
    
    return results


def calculateVegetationMetrics(image, zone, scale, simplify_tolerance=1.5):
    # Vectorisation des surfaces
    vectors = image.select('VEGETATION').reduceToVectors(
        geometry = zone.geometry(),
        scale = scale,
        eightConnected = True,
        maxPixels = 1e12,
        geometryType = 'polygon')
    
    # Séparer les surfaces végétation du reste
    vector_vegetation = vectors.filter("label == 1")
    
    # Simplifier les géométries pour le périmètre.
    geom_vegetation = vector_vegetation.geometry().simplify(scale*simplify_tolerance)

    # Calculer les percentiles de taille de polygones
    veget_percentiles = vector_vegetation.aggregate_array('count').reduce(ee.Reducer.percentile(
        percentiles=list(range(0,110,10)),
        outputNames=[f'VEGETATION_POLYGONS_p{pc}' for pc in range(0,110,10)]
    ))

    # Initialisation du dictionnaire des résultats
    results = ee.Dictionary(veget_percentiles).combine(ee.Dictionary({
        # Calculer le nombre de polygones
        'VEGETATION_POLYGONS': vector_vegetation.size(),

        # Calculer l'aire des surfaces végétation
        'VEGETATION_AREA': image.select('VEGETATION').reduceRegion(
            reducer = ee.Reducer.sum(),
            geometry = vector_vegetation,
            scale = scale
        ).getNumber('VEGETATION'),
        
        # Calucler les périmètres
        'VEGETATION_PERIMETER': geom_vegetation.perimeter(scale),
        
        # Calcul du ndvi moyen des surfaces végétation
        'MEAN_VEGETATION_NDVI': image.select('NDVI').reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = vector_vegetation,
            scale = scale
            ).getNumber('NDVI'),
        
        # Calcul du mndwi moyen des surfaces végétation
        'MEAN_VEGETATION_MNDWI': image.select('MNDWI').reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = vector_vegetation,
            scale = scale
            ).getNumber('MNDWI'),
        
        # Calcul du ndvi moyen de tout le ZONE
        'MEAN_NDVI': image.select('NDVI').reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = zone.geometry(),
            scale = scale
            ).getNumber('NDVI'),
    }))
        
    return results


def calculateACMetrics(image, zone, scale, simplify_tolerance=1.5):
    # Vectorisation des surfaces
    vectors = image.select('AC').reduceToVectors(
        geometry = zone.geometry(),
        scale = scale,
        eightConnected = True,
        maxPixels = 1e12,
        geometryType = 'polygon')
    
    # Séparer les surfaces végétation du reste
    vector_ac = vectors.filter("label == 1")
    
    # Initialisation du dictionnaire des résultats
    results = ee.Dictionary({
        # Calculer l'aire des surfaces végétation
        'AC_AREA': image.select('AC').reduceRegion(
            reducer = ee.Reducer.sum(),
            geometry = vector_ac,
            scale = scale
        ).getNumber('AC'),
        
        # Calcul du ndvi moyen des surfaces végétation
        'MEAN_AC_NDVI': image.select('NDVI').reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = vector_ac,
            scale = scale
            ).getNumber('NDVI'),
        
        # Calcul du mndwi moyen des surfaces végétation
        'MEAN_AC_MNDWI': image.select('MNDWI').reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = vector_ac,
            scale = scale
            ).getNumber('MNDWI'),
    })

    return results


def zoneMetrics(collection, scale=30):
    def mapZONE(zone):
        # Filtrer la collection d'images sur l'emprise du ZONE traité
        zone_images_collection = collection.filterBounds(zone.geometry())

        # Définir une fonction qui ajoute les métriques d'une image à la liste des métriques du ZONE
        def addMetrics(image, metrics_list):
            # Récupérer la Feature du ZONE qui est stocké dans le premier élément de la liste
            zone = ee.Feature(ee.List(metrics_list).get(0))
            
            # Calculer les métriques
            cloud_score = calculateCloudScore(image, zone, scale)
            coverage_score = calculateCoverage(image, zone, scale)
            water_metrics = calculateWaterMetrics(image, zone, scale)
            vegetation_metrics = calculateVegetationMetrics(image, zone, scale)
            ac_metrics = calculateACMetrics(image, zone, scale)
            
            # Créer un dictionnaire avec toutes les métriques
            image_metrics = zone.set(ee.Dictionary({
                                     'DATE': ee.Date(image.get('system:time_start')).format("YYYY-MM-dd"),
                                     'CLOUD_SCORE': cloud_score, 
                                     'COVERAGE_SCORE': coverage_score,
                                     'SCALE': ee.Number(scale),
                                    }).combine(water_metrics).combine(vegetation_metrics).combine(ac_metrics))
            
            # Filtrer si le ZONE est 100% couvert de nuages
            output_list = ee.Algorithms.If(ee.Number(cloud_score).gte(ee.Number(100)), ee.List(metrics_list), ee.List(metrics_list).add(image_metrics))
            
            # Ajouter ce dictionnaire à la liste des métriques
            return output_list

        # Stocker le ZONE traité dans le premier élément de la liste
        first = ee.List([zone])

        # Ajouter les métriques calculées sur chaque image à la liste
        metrics = zone_images_collection.iterate(addMetrics, first)

        # Supprimer le ZONE traité de la liste pour alléger le résultat
        metrics = ee.List(metrics).remove(zone)

        # Renvoyer la Feature en ajoutant l'attribut metrics
        return zone.set({'metrics': metrics})
    return mapZONE


def calculateZONEsMetrics(collection, zones, scale=30):
    # Ajouter les listes de métriques aux attributs des ZONEs
    metrics = zones.map(zoneMetrics(collection, scale))

    # Dé-empiler les métriques stockées dans un attribut de la FeatureCollection
    unnested = ee.FeatureCollection(metrics.aggregate_array('metrics').flatten())

    # Retourner uniquement les métriques (pas la Feature complète)
    return unnested

