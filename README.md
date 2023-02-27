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

# TODO

- [ ] Add AOI surface / Image coverage
- [ ] Fix cloud score
- [ ] Optimize DGO metrics mapping