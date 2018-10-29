#! /bin/bash

# Environment dependencies
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
# CDS_API_URL, e.g., url: https:/unknown
# CDS_API_KEY, e.g., key: 123111

# Initialise s3 bucket, with access key, password available in environment variable.
# Mount s3 bucket under /s3bucket
# This relies on environment variable to have been set
s3fs ec2-us-east-1-oikolab /s3bucket

# Initialise
touch ~/.cdsapirc
echo $CDS_API_URL > ~/.cdsapirc
echo $CDS_API_KEY >> ~/.cdsapirc

gunicorn app:server -b :8000 --chdir /src/