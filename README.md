# GEE water extraction

# Installation

- Windows
```bash
python -m venv env --prompt ee-water-extraction
.\env\Scripts\activate
python -m pip install -U pip
python -m pip install -e .
```

- Linux
```bash
python -m venv env --prompt ee-water-extraction
source env/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

# Example usage

```python
# Import packages
import ee
from eewaterextraction.workflows import dgos_properties_to_csv

# Authentificate using your preferred method
credentials = ee.ServiceAccountCredentials('ee-water-extraction@earthengine-371715.iam.gserviceaccount.com', 
                                           './earthengine-key.json')
ee.Initialize(credentials)

# Run the dgos_properties_to_csv workflow for some DGOs
dgos_properties_to_csv(
    dgo_shapefile_path = './example_data/Lhasa_RC_DGO2km_updated.shp', 
    output_csv = './example_data/properties.csv',
    dgo_list = [1,5,30])

# Run the dgos_properties_to_csv workflow for all DGOs
dgos_properties_to_csv(
    dgo_shapefile_path = './example_data/Lhasa_RC_DGO2km_updated.shp', 
    output_csv = './example_data/properties.csv')
```