"""
This defines the file naming convention for naming and location of a weather file.
WeatherFile operates in 2 modes: file, s3. If WeatherFile operates in S3, it assumes the environment includes ACCESS_KEY_ID,
and SECRET_KEY information.
"""
import os
from collections import deque

import boto3
import botocore
from boto3.s3.transfer import TransferConfig
from botocore.config import Config


class WeatherFile:
    """in s3 mode, files are located via s3 boto3 library """
    MODE_S3 = 's3'

    """in file mode, files are located through folder lookups """
    MODE_FILE = 'file'

    def __init__(self, prefix_path: str):
        """
        Constructor

        :param prefix_path: specifies the path where weather files are located, and shall be saved to
                            if the prefix path starts as `s3://`, then weather file will use the s3
                            boto3 client to connect for locating files
        """
        if not prefix_path.endswith('/'):
            prefix_path = prefix_path + '/'

        self.mode = self.MODE_FILE
        self.data_path = prefix_path

        if prefix_path.startswith('s3://'):
            self.mode = WeatherFile.MODE_S3
            data_paths = prefix_path.split('/')
            if len(data_paths) < 2:
                raise Exception('data path is invalid')
            path_deque = deque(prefix_path)
            self.bucket = path_deque.popleft()
            self.data_path = '/'.join(path_deque)

            TransferConfig(max_concurrency=5)
            self.client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                                       aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                                       config=Config(signature_version=botocore.UNSIGNED))
        """ File extension for reading original weather files """
        self.file_extension = 'grb'

    def get_or_create_original_folder(self, year):
        """
        This retrieves the path to where original weather data shall be stored. It's per year.

        :param year: str
        :return: str
        """
        directory = "%s%s/" % (self.data_path, str(year))
        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory

    def get_original_folder(self, year):
        """
        This returns the folder path for the given year where user can locate the original data sets.

        :param year: str
        :return: str
        """
        if self.mode == WeatherFile.MODE_FILE:
            directory = "%s%s/" % (self.data_path, str(year))
            if not os.path.exists(directory):
                raise Exception('Original file for %s cannot be found' % directory)
            return directory


    def get_processed_file_name(self, year, month, iso3, city):
        """
        This returns the convention of a weather file given a year-month, and country(iso3), and its city

        :param year:
        :param month:
        :param iso3:
        :param city:
        :return: str
        """
        file_name = '%d-%02d-%s_%s.nc' % (year, month, iso3, city)
        file_name = file_name.replace(' ', '_').lower()
        return file_name

    def get_original_file_extension(self):
        """
        This returns the file extension used on original weather file
        :return: str
        """
        return self.file_extension

    def get_original_file_name(self, year, month, parameter):
        """
        This returns whether original weather file shall be processed

        :param year:
        :param month:
        :param parameter:
        :return: str
        """
        filename = '%s_%d_%02d_era5.%s' % (parameter, year, month, self.file_extension)
        return filename

    def get_original_data_set_path(self, year, month, parameter_name):
        """
        This returns the path to a ECMWF original data set for a variable, month & year.

        :param year:
        :param month:
        :param parameter_name:
        :return: str path indicating the where the weather could be found.
        """
        data_file = self.get_or_create_original_folder(year) + self.get_original_file_name(year, month, parameter_name)

        if not os.path.isfile(data_file):
            raise Exception(data_file + ' does not exist')

        return data_file

    def get_processed_data_set_path(self, year, month, country_iso3, city_name):
        """
        Based on the information given, and the configured data_path for this weather file. It returns the file path
        where a processed weather file shall be stored at.

        :param year: int
        :param month: int
        :param country_iso3: str
        :param city_name: str
        :return:
        """
        output_folder = '%s%s/%s/' % (self.data_path, 'processed', year)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        full_path = output_folder + self.get_processed_file_name(year, month, country_iso3,
                                                                 city_name.lower())
        return full_path
