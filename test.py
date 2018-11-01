"""
A command prompt CLI to help ingest new data
"""
import argparse
import os

import boto3
import botocore
from boto3.s3.transfer import TransferConfig

from api.core.weather_file import WeatherFile
from api.core.weather_parameter import WeatherParameter
from api.ingest.preprocessor import Preprocessor


def _copy_file_from_s3(s3_client, year, month):
    parameters = WeatherParameter.get_all_parameters()
    weather_file = WeatherFile(data_path='/s3bucket/')
    destination_folder = '/nvm/%s/' % year

    for parameter in parameters:
        weather_file_path = weather_file.get_original_file_name(year, month, parameter)

        weather_file_full_path = "%s/%s" % (year, weather_file_path)
        destination_file = destination_folder + weather_file_path
        if os.path.exists(destination_file):
            print("File already exists: %s" % destination_file)
            continue

        print('Downloading %s to %s' % (weather_file_full_path, destination_file))
        _download_file(s3_client, weather_file_full_path, destination_file)


def _download_file(s3_client, from_path, to_path):
    bucket = 'ec2-us-east-1-oikolab'
    s3_client.download_file(bucket, from_path, to_path)


def _remove_files(year, month):
    parameters = WeatherParameter.get_all_parameters()
    weather_file = WeatherFile(data_path='/s3bucket/')
    destination_folder = '/nvm/'

    for parameter in parameters:
        weather_file_path = weather_file.get_original_file_name(year, month, parameter)

        destination_file = destination_folder + weather_file_path
        print('removing files: ' + destination_file)


def main_procedure(min_month, max_month, year):
    bucket = 'ec2-us-east-1-oikolab'
    TransferConfig(max_concurrency=5)
    client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                          config=botocore.client.Config(signature_version=botocore.UNSIGNED))

    for current_month in range(min_month, max_month + 1):
        await _copy_file_from_s3(client, year, current_month)

        preprocessor = Preprocessor('/nvm/')
        for month in range(min_month, max_month + current_month):
            print('processing for %s/%s' % (year, month))
            preprocessor.process(year=year, month=current_month)

        await _remove_files(year, current_month)


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

    # Argument extraction
    args = parser.parse_args()
    arg_year = args.year
    arg_data_path = args.path
    arg_min_month = min(1, args.min_month)
    arg_max_month = max(12, args.max_month)

    # Copy the files over first
    main_procedure(arg_min_month, arg_max_month, arg_year)

