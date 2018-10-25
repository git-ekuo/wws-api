## Introduction
A simple weather web service API, for energy related analysis.

## Installation

##### MacOS
- Install [Homebrew](https://brew.sh/)
- Install system libraries required: `brew install nco netcdf hdf5`
- Run `Set environment - export HDF5_DIR=/usr/local/Cellar/hdf5/1.10.2_1`
- Install Python 3.7

- Create virtualenv inside the current project folder `python3.7 -m venv venv`
- Active the virtual env `source venv/bin/activate`
- Run `pip install -r requirements.txt`

##### Docker
- Install Docker
- Run `docker run -it itekuo/python-data-docker bash`

##### File Structure
    .
    ├── docker                  # Dockerfile for a base image published to itekuo/python-data-docker.
    ├── api                     # Source code
    ├── data                    # folder for storing data files that are needed by this repository
    ├── jupyter                 # Collection of jupyter notebooks for data exploration
    ├── Dockerfile              # Dockerfile for elastic beanstalk, has its base from itekuo/python-data-docker
    ├── package.json            # Npm dependency for setting up orca (snapshot) required by plotly
    ├── LICENSE
    └── README.md


