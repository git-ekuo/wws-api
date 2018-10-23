## Introduction
To provide analytics on energy usage, and empoewr users to make wise decisions.

## Installation

##### MacOS
- Install [Homebrew](https://brew.sh/)
- Install system libraries required: `brew install nco netcdf hdf5`
- Run `Set environment - export HDF5_DIR=/usr/local/Cellar/hdf5/1.10.2_1`
- Install Python 3.7

- Create virtualenv inside the current project folder `python3.7 -m venv venv`
- Active the virtual env `source venv/bin/activate`
- Run `pip install -r requirements.txt`