#! /bin/bash

# Initialise s3 bucket, with access key, password available in environment variable.
# Mount s3 bucket under /s3bucket
s3fs ec2-us-east-1-oikolab /s3bucket

gunicorn app:server -b :8000 --chdir /src/