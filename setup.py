import os
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '0.1.0'
try:
    VERSION = os.environ['PYGS_VERSION']
except KeyError:
    pass

setup(
    name='nrtpygs',
    version=VERSION,
    description='NRT Generic Services Python Package',
    author="Joao Bento",
    author_email="j.p.dasilvabento@ljmu.ac.uk",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pika==1.3.2",
        "pytest==7.4.3",
        "python-statemachine==2.1.2",
        "redis==5.0.1",
        "influxdb-client==1.39.0",
    ]
)
