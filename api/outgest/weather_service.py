"""
This reads NetCDF ECMWF ERA5 datasets (processed by `preprocessor.py`) from a pre-configured S3 bucket.
"""

import xarray

from api.city.city_service import CityService
from api.core.weather_file import WeatherFile


class WeatherService:
    def __init__(self, data_path):
        """
        Constructor

        :param data_path: str, root path to the processed weather data
        """
        self.city_service: CityService = CityService()
        self.weather_file: WeatherFile = WeatherFile(data_path)

    def _get_city(self, city_name):
        city_list = self.city_service.get_city_coordinates()
        cities = city_list.loc[city_list["city"] == city_name]
        if cities.empty:
            raise Exception('Cannot find your city')

        for city in cities.itertuples():
            return city

    def _get_data_set(self, local_year, local_month, city_name):
        local_city = self._get_city(city_name)
        full_path = self.weather_file.get_processed_data_set_path(local_year, local_month, local_city.iso3, local_city.city)

        ds = xarray.open_dataset(full_path)
        return ds

    def get_weather_data_set(self, year, month, city):
        """
        This retrieves processed weather data and returns the xarray data set.

        :param year: int
        :param month: int
        :param city: str
        :return: xarray.Dataset
        """
        return self._get_data_set(year, month, city)
