"""
This defines the file naming convention for naming and location of a weather file
"""
import os


class WeatherFile:

    def __init__(self, data_path: str):
        """
        Constructor

        :param data_path: specifies the path where weather files are located, and shall be saved to
        """
        self.data_path = data_path
        """ File extension for reading original weather files """
        self.file_extension = 'grb'

    def get_or_create_original_folder(self, year):
        """
        This retrieves the path to where original weather data shall be stored. It's per year.

        :param year: str
        :return: str
        """
        directory = "/%s/%s/" % (self.data_path, str(year))
        if not os.path.exists(directory):
            os.makedirs(directory)

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
