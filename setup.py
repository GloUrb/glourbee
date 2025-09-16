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
        'rasterio',
        'scikit-image',
        'earthengine-api',
        'pandas',
        'geemap',
        'geedim',
        'cryptography',
        'geetools==0.6.14', # mosaicSameDay deprecated in 1.0.0 :(
        'streamlit>=1.49.0',
        'leafmap',
        'psycopg2-binary',
        'sqlalchemy',
        'alembic',
        'geoalchemy2',
        'redis',
        'celery[redis]'
    ],
)