from setuptools import setup

setup(
    name='GloUrbEE',
    version='0.2',
    py_modules=['glourbee.*'],
    install_requires=[
        'click',
        'numpy',
        'geopandas',
        'earthengine-api',
        'pandas',
        'geemap',
        'geetools',
        'ipython',
        'ipykernel',
        'ipyleaflet==0.16',
        'streamlit',
        'streamlit-folium'
    ],
)