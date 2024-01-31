# GloUrbEE - Extract GloUrb metrics and indicators from Google Earth Engine

# Installation

- Windows
```powershell
python -m venv env --prompt glourbee
.\env\Scripts\activate
python -m pip install -U pip
python -m pip install -e .
```

- Linux
```bash
python -m venv env --prompt glourbee
source env/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

# Example usage

The `notebook.ipynb` file contains example of how to use the GloUrbEE tool.

# Start the UI

The GloUrbEE-UI allow you to use the main GloUrbEE package workflow with a fancy user-friendly interface.
The first time you start the UI, you'll had to create the database and run migrations:
```bash
sudo apt-get install sqlite3

sqlite3 ui/lib/db/glourbee-ui.db
sqlite> .quit

alembic upgrade
```

Then, to start the UI:
- Windows
```powershell
.\env\Scripts\activate
streamlit run ui/00_🏠_HomePage.py
```

- Linux
```bash
source env/bin/activate
streamlit run ui/00_🏠_HomePage.py
```

# Data extracted
## Metrics
| metric name | description |   
|---|---|
| AC_AREA | Active Channel area (pixels) |
| CLOUD_SCORE | Percent of the DGO covered by clouds (%) |
| COVERAGE_SCORE | Percent of the DGO covered by the Landsat image (%) |
| MEAN_AC_MNDWI | Mean MNDWI in the active channel surface |
| MEAN_AC_NDVI | Mean NDVI in the active channel surface |
| ~~MEAN_DRY_MNDWI~~ | ~~Mean MNDWI in the surface which is not water~~  |
| MEAN_MNDWI | Mean MNDWI of the full DGO |
| MEAN_NDVI| Mean NDVI of the full DGO |
| MEAN_VEGETATION_MNDWI | Mean MNDWI in the vegetation surface |
| MEAN_VEGETATION_NDVI | Mean NDVI in the vegetation surface |
| MEAN_WATER_MNDWI | Mean MNDWI in the water surface |
| VEGETATION_AREA | Vegetation area (pixels) |
| VEGETATION_POLYGONS | Number of vegetation patches inside the DGO |
| VEGETATION_POLYGONS_p* | Percentiles of the vegetation patches size (in pixels) inside the DGO |
| VEGETATION_PERIMETER | Vegetation surface perimeter (projection unit) |
| WATER_AREA | Water area (pixels) |
| WATER_POLYGONS | Number of water patches inside the DGO |
| WATER_POLYGONS_p* | Percentiles of the water patches size (in pixels) inside the DGO |
| WATER_PERIMETER | Water surface perimeter (projection unit) |

## Indicators
| indicator name | description |   
|---|---|
| occurrence_p* | The frequency with which water was present (JRC Global Surface Water Mapping) |
| change_abs_p* | Absolute change in occurrence between two epochs: 1984-1999 vs 2000-2021 (JRC Global Surface Water Mapping) |
| change_norm_p* | Normalized change in occurrence. (epoch1-epoch2)/(epoch1+epoch2) * 100 (JRC Global Surface Water Mapping) |
| seasonality_p* | Number of months water is present (JRC Global Surface Water Mapping) |
| recurrence_p* | The frequency with which water returns from year to year (JRC Global Surface Water Mapping) |
| max_extent | Surface where water has ever been detected (JRC Global Surface Water Mapping) |

# TODO
- Changer le filtre modal par un tamisage
- Ajouter *transition* du JRC Surface Water
- Récupérer tous les champs du shapefile en entrée pour les métriques (indicateurs OK)
- Gérer les polygones de grande taille au niveau des métriques (indicateurs OK)
