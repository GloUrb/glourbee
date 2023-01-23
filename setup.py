from setuptools import setup

setup(
    name='EeWaterExtraction',
    version='0.1',
    py_modules=['eewaterextraction.*'],
    install_requires=[
        'click',
        'numpy',
        'earthengine-api',
        'pandas',
        'geemap',
        'ipython'
    ],
)