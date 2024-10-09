from setuptools import setup
from glourbee import __version__

setup(
    name='glourbee',
    version=__version__,
    py_modules=['glourbee.*'],
    install_requires=[
        'click',
        'numpy',
        'geopandas',
        'earthengine-api',
        'pandas',
        'geemap',
        'geetools==0.6.14', # mosaicSameDay deprecated in 1.0.0 :(
        # 'ipython',
        # 'ipykernel',
        # 'ipyleaflet==0.16',
        'streamlit>=1.35.0',
        'streamlit-folium',
        'sqlalchemy',
        'alembic',
        'debugpy',
    ],
)