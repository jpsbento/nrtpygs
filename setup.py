from setuptools import setup, find_packages
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '0.1.0'
try:
    version = os.environ['PYGS_VERSION']
except KeyError:  # bamboo_buildNumber isn't defined, so we're not running in Bamboo
    pass

setup(
    name='nrtpygs',
    version=version,
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
        "pika==1.1.0",
        "pytest==6.2.1",
        "python-statemachine==0.8.0",
        "redis==4.3.4",
        "timeout_decorator==0.5.0",
    ]
)