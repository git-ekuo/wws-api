"""
This reads ECMWF ERA5 reanalysis dataset (from a pre-defined path) and generates yearly ERA5 (in NetCDF format)
for major cities and locations.

This depends on `data/simplemaps-worldcities-basic.csv` to identify a set of major cities in the world.

Generated files is structured as [year]/[month]/[year-month-variable]_era5.nc
"""
import datetime

import xarray
import numpy as np

from api.city.city_service import CityService
from api.core.weather_file import WeatherFile
from api.core.weather_parameter import WeatherParameter


class Preprocessor:

    def __init__(self, data_path):
        """

        :param data_path: str specifies the root folder where weather file shall be located
        """
        self.weather_file = WeatherFile(data_path)
        self.city_service = CityService()

    def preprocess(self, d_year, d_data_path):
        city_list = self.city_service.get_city_coordinates()
        for d_month in range(1, 13):
            data_sets = []
            try:
                print('Processing files for %d-%d in %s' % (d_year, d_month, d_data_path))
                for parameter in WeatherParameter.get_all_parameters():
                    data_sets.append(self._get_netcdf_to_process(d_year, d_month, parameter, d_data_path))

                count = 0
                for city in city_list.itertuples():
                    if count % 1000 == 0:
                        print('Processed %s cities so far [%s]' % (count, datetime.datetime.now()))
                    city_by_month_ds = self._merge_by_city(city, data_sets)

                    full_path = self.weather_file.get_processed_data_set_path(d_year, d_month, city.iso3, city.city)
                    city_by_month_ds.to_netcdf(full_path, mode='w', compute=True)
                    count = count + 1
            finally:
                for data_set in data_sets:
                    data_set.close()

    def _get_netcdf_to_process(self, local_year, local_month, local_parameter):
        data_file = self.weather_file.get_original_data_set_path(local_year, local_month, local_parameter)
        ds = xarray.open_dataset(data_file)
        return ds

    def _merge_by_city(self, city, data_sets):
        all_variables = []
        for data_set in data_sets:
            lat = city.lat
            lon = city.lon
            if city.lon > 0:
                data_set = data_set.sel(latitude=slice(np.floor(lat * 4 + 1) / 4, np.floor(lat * 4) / 4),
                                        longitude=slice(np.floor(lon * 4) / 4 % 360, np.floor(lon * 4 + 1) / 4 % 360))
            elif 0 > city.lon > -0.25:
                data_set = data_set.roll(longitude=1)
                data_set = data_set.sel(latitude=slice(np.floor(lat * 4 + 1) / 4, np.floor(lat * 4) / 4),
                                        longitude=slice(np.floor(lon * 4) / 4 % 360, np.floor(lon * 4 + 1) / 4 % 360))

            one_variable_ds = data_set.interp(latitude=lat, longitude=lon % 360)

            all_variables.append(one_variable_ds)

        return xarray.merge(all_variables)
