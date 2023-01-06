import ee
from .classification import extractWater


def vectorizeWater(selected_dgo, landsat_scale, px_simplify_tolerance):
    def mapImage(mndwi):
        # Seuillage du raster
        raster_water = extractWater(mndwi)
        
        # Vectorisation du seuillage
        vectors = raster_water.reduceToVectors(
            geometry = selected_dgo.geometry(),
            scale = landsat_scale,
            eightConnected = True,
            maxPixels = 1e12,
            geometryType = 'polygon')
        
        # Séparer les surfaces en eau et les surfaces émergées
        vector_water = vectors.filter("label == 1")
        vector_dry = vectors.filter("label == 0")
        
        # Calculer l'aire des surfaces en eau
        water_area = raster_water.reduceRegion(
            reducer = ee.Reducer.sum(),
            geometry = vector_water,
            scale = landsat_scale
        )
        
        # Simplifier les géométries
        geoms_water = vector_water.geometry().simplify(landsat_scale*px_simplify_tolerance)
        
        # Calucler les périmètres
        water_perimeter = geoms_water.perimeter(landsat_scale)
        
        # Calcul du mndwi moyen des surfaces en eau
        mean_water_mndwi = mndwi.reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = vector_water,
            scale = landsat_scale
            )
        
        # Calcul du mndwi moyen des surfaces émergées
        mean_dry_mndwi = mndwi.reduceRegion(
            reducer = ee.Reducer.mean(),
            geometry = vector_dry,
            scale = landsat_scale
            )
        
        raster_water = raster_water.set({'DGO_FID': selected_dgo.get('DGO_FID'),
                                        'DATE_ACQUIRED': mndwi.get('DATE_ACQUIRED'),
                                        'MEAN_WATER_MNDWI': mean_water_mndwi.get('MNDWI'),
                                        'MEAN_DRY_MNDWI': mean_dry_mndwi.get('MNDWI'),
                                        'WATER_AREA': water_area.get('WATER'),
                                        'WATER_PERIMETER': water_perimeter})
        
        return raster_water
    return mapImage