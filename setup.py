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
        'geedim',
        'geetools==0.6.14', # mosaicSameDay deprecated in 1.0.0 :(
        # 'ipython',
        # 'ipykernel',
        # 'ipyleaflet==0.16',
        'streamlit>=1.49.0',
        'leafmap',
        'psycopg2-binary',
        'sqlalchemy',
        'geoalchemy2',
        # 'alembic',
        # 'debugpy',
        # 'authlib>=1.3.2',
        'redis',
        'celery[redis]'
    ],
)