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

The `notebook.ipynb` file contains example of how to use the ee-waterextraction tool.

# Data extracted
## Metrics
| metric name | description |   
|---|---|
| AC_AREA | Active Channel area (pixels) |
| CLOUD_SCORE | Percent of the DGO covered by clouds (%) |
| COVERAGE_SCORE | Percent of the DGO covered by the Landsat image (%) |
| MEAN_AC_MNDWI | Mean MNDWI in the active channel surface |
| MEAN_AC_NDVI | Mean NDVI in the active channel surface |
| MEAN_DRY_MNDWI | Mean MNDWI in the surface which is not water  |
| MEAN_MNDWI | Mean MNDWI of the full DGO |
| MEAN_NDVI| Mean NDVI of the full DGO |
| MEAN_VEGETATION_MNDWI | Mean MNDWI in the vegetation surface |
| MEAN_VEGETATION_NDVI | Mean NDVI in the vegetation surface |
| MEAN_WATER_MNDWI | Mean MNDWI in the water surface |
| VEGETATION_AREA | Vegetation area (pixels) |
| VEGETATION_PERIMETER | Vegetation surface perimeter (projection unit) |
| WATER_AREA | Water area (pixels) |
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
- Nombre de polygones par classe par DGO
- Quartiles, Moyenne et D90 de la surface de ces polygones
- Changer le filtre modal par un tamisage
- Ajouter JRC Surface Water par DGO (```ee.Image("JRC/GSW1_4/GlobalSurfaceWater")```)