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

# Metrics extracted

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
