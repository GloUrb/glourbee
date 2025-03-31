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

## With streamlit 

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

## With docker

```bash
docker run --expose 8501 ghcr.io/evs-gis/glourbee-ui:latest 
```

The application should be available at http://localhost:8501

# Data extracted
## Metrics
| metric name | description |   
|---|---|
| AC_AREA | Active Channel area (pixels) |
| CLOUD_SCORE | Percent of the ZONE covered by clouds (%) |
| COVERAGE_SCORE | Percent of the ZONE covered by the Landsat image (%) |
| SCALE | Size of a pixel on the selected imagery dataset (meters) |
| MEAN_AC_MNDWI | Mean MNDWI in the active channel surface |
| MEAN_AC_NDVI | Mean NDVI in the active channel surface |
| ~~MEAN_DRY_MNDWI~~ | ~~Mean MNDWI in the surface which is not water~~  |
| MEAN_MNDWI | Mean MNDWI of the full ZONE |
| MEAN_NDVI| Mean NDVI of the full ZONE |
| MEAN_BSI | Mean BSI (Bare Soil Index) of the full zone |
| MEAN_VEGETATION_MNDWI | Mean MNDWI in the vegetation surface |
| MEAN_VEGETATION_NDVI | Mean NDVI in the vegetation surface |
| MEAN_WATER_MNDWI | Mean MNDWI in the water surface |
| VEGETATION_AREA | Vegetation area (pixels) |
| VEGETATION_POLYGONS | Number of vegetation patches inside the ZONE |
| VEGETATION_POLYGONS_p* | Percentiles of the vegetation patches size (in pixels) inside the ZONE |
| VEGETATION_PERIMETER | Vegetation surface perimeter (projection unit) |
| WATER_AREA | Water area (pixels) |
| WATER_POLYGONS | Number of water patches inside the ZONE |
| WATER_POLYGONS_p* | Percentiles of the water patches size (in pixels) inside the ZONE |
| WATER_PERIMETER | Water surface perimeter (projection unit) |

### How the masks are extracted
To extract the water, active channel and vegetation masks, the following expressions are proposed as default parameters depending of the selected imagery.
You can define custom ones using the `workflow.startWorflow()` `watermask_expression`, `activechannel_expression` and `vegetation_expression` parameters. The available layers for expressions are:`BLUE`,`GREEN`,`RED`,`NIR`,`SWIR1`,`SWIR2`,`MNDWI`,`NDWI`,`NDVI`.

##### Landsat imagery default masks
```py
watermask_expression = 'MNDWI > 0.0'
activechannel_expression = 'MNDWI > -0.4 && NDVI < 0.2'
vegetation_expression = 'NDVI > 0.15'
```

##### Sentinel-2 imagery default masks
```py
watermask_expression = 'NDWI > -0.1'
activechannel_expression = 'NDWI > -0.4 && NDVI < 0.2'
vegetation_expression = 'NDVI > 0.15'
```

## Indicators
| indicator name | description |   
|---|---|
| occurrence_p* | The frequency with which water was present (JRC Global Surface Water Mapping) |
| change_abs_p* | Absolute change in occurrence between two epochs: 1984-1999 vs 2000-2021 (JRC Global Surface Water Mapping) |
| change_norm_p* | Normalized change in occurrence. (epoch1-epoch2)/(epoch1+epoch2) * 100 (JRC Global Surface Water Mapping) |
| seasonality_p* | Number of months water is present (JRC Global Surface Water Mapping) |
| recurrence_p* | The frequency with which water returns from year to year (JRC Global Surface Water Mapping) |
| max_extent | Surface where water has ever been detected (JRC Global Surface Water Mapping) |

# Credits
Many thanks to:
- [Barbara Belletti](https://github.com/bbelletti) for the original concept and ideas
- Khalid for the first Python version
- [Louis Rey](https://github.com/LouisRey74) for huge testing
- [Julie Limonet](https://github.com/Julielmnt) for the UI skeleton
- [Leo Helling](https://github.com/jlhelling) for the Sentinel-2 integration
- [Samuel Dunesme](https://github.com/sdunesme)

# Citation 
[![DOI](https://zenodo.org/badge/578546372.svg)](https://zenodo.org/doi/10.5281/zenodo.11235572)

Dunesme, S., Belletti, B., Helling, L., & Limonet, J. (2024). EVS-GIS/glourbee. UMR5600 Environnement, Ville, Société. https://doi.org/10.5281/zenodo.11235572
