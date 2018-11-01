"""
A command prompt CLI to help ingest new data
"""
import argparse
import os
import sys

import boto3
import botocore
from boto3.s3.transfer import TransferConfig

from api.core.weather_file import WeatherFile
from api.core.weather_parameter import WeatherParameter
from api.ingest.preprocessor import Preprocessor


def _copy_file_from_s3(s3_client, year, month):
    parameters = WeatherParameter.get_all_parameters()
    weather_file = WeatherFile(data_path='/s3bucket/')
    destination_folder = '/nvm/'

    for parameter in parameters:
        weather_file = weather_file.get_original_file_name(year, month, parameter)

        weather_file_key = weather_file.get_original_folder(year) + weather_file
        destination_file = destination_folder + weather_file_key
        print('metadata_key: ' + weather_file_key)
        print('metadata_key: ' + destination_file)
        s3_client.download_file(bucket, weather_file_key, weather_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pre-process files for year-month combination')
    parser.add_argument('year', type=int, help='an integer representing the year, e.g., 2017')
    parser.add_argument('min_month', type=int,
                        help='the month from which preprocessing starts, e.g., 1 for january (inclusive)')
    parser.add_argument('max_month', type=int,
                        help='the month from which preprocessing finishes, e.g., 2 for februrary (inclusive)')
    parser.add_argument('path', help='a string indicating the system path leading to where the data is. '
                                     'e.g., /s3bucket/')

    # Initialise S3
    bucket = 'ec2-us-east-1-oikolab'
    TransferConfig(max_concurrency=5)
    client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                          config=botocore.client.Config(signature_version=botocore.UNSIGNED))

    for path in sys.path:
        print('path: ' + path)

    # Argument extraction
    args = parser.parse_args()
    year = args.year
    data_path = args.path
    min_month = min(1, args.min_month)
    max_month = max(12, args.max_month)

    # Copy the files over first
    _copy_file_from_s3(client, 2016, 1)

    # # Go through the months as specified
    preprocessor = Preprocessor(data_path)
    for month in range(min_month, max_month + 1):
        print('processing for %s/%s' % (year, month))
        preprocessor.process(year=year, month=month)
