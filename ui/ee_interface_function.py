#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ee
import geemap
import tempfile

# from eewaterextraction import data_management
# from eewaterextraction import classification
# from eewaterextraction import visualization
# from eewaterextraction import dgo_metrics
from eewaterextraction import assets_management

def temp_file_path(uploaded_file) :
    temp_file = tempfile.NamedTemporaryFile(delete=False)

    # Write uploaded file content to the temporary file
    temp_file.write(uploaded_file.read())

    # Get the path of the temporary file
    uploaded_file_path = temp_file.name

    # Close the temporary file
    temp_file.close()
    return(uploaded_file_path)


def credentials(mail = 'jlimonet@ee-glourb.iam.gserviceaccount.com', key1 = './ee-glourb-58e556f00841.json' , key2 = './ee-glourb-58e556f00841.json'):
    if key1 != "":
        try:
            credentials = ee.ServiceAccountCredentials(mail, key1)
            ee.Initialize(credentials)
            # If initialization is successful, print a success message
            return(True)
            
        except ee.EEException as e:
            # If an exception occurs during initialization, print the error message
            return(False)
        
    if key2 != "":
        try:
            credentials = ee.ServiceAccountCredentials(mail, key2)
            ee.Initialize(credentials)
            # If initialization is successful, print a success message
            return(True)
            
        except ee.EEException as e:
            # If an exception occurs during initialization, print the error message
            return(False)


def assets(DGO = './example_data/Lhasa_RC_DGO2km_updated_gcs.shp' , ee_project_name = 'ee-glourb'):
    dgo_assetId, dgo_features = assets_management.uploadDGOs(DGO, ee_project_name=ee_project_name, simplify_tolerance=15)
    return(dgo_assetId, dgo_features)

def plot_map(dgo_features):
    Map = geemap.Map(language='en')
    # Add the DGO features as a layer to the map
    Map.addLayer(dgo_features, {}, 'DGO Features')

    # Display the map
    Map.centerObject(dgo_features, 10)  # Center the map on the DGO features
    Map.addLayerControl()  # Add layer control if needed
    return(Map)


def run():
    pass
if __name__ == '__main__':
    run()