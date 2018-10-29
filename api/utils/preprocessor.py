"""
This reads ECMWF ERA5 reanalysis dataset (from a pre-defined path) and generates yearly ERA5 (in NetCDF format)
for major cities and locations.

This depends on `data/simplemaps-worldcities-basic.csv` to identify a set of major cities in the world.

Generated files is structured as [year]/[month]/[year-month-variable]_era5.nc
"""
import argparse
import datetime
import os

import pandas as pd
import xarray


def _get_city_coordinates():
    """

    :return:
    """
    city_list = pd.read_csv(os.path.join('data', 'simplemaps-worldcities-basic.csv'))
    city_list = city_list.sort_values('lat', ascending=True)
    city_list = city_list.sort_values('lng', ascending=True)
    city_list = city_list.rename(columns={'lat': 'lat', 'lng': 'lon'})
    # city_list = city_list.drop(['city_ascii', 'pop', 'iso2', 'iso3', 'province'])
    return city_list


def _get_netcdf_to_process(local_year, local_month, local_parameter, local_data_path):
    """
    
    :param local_year: 
    :param local_month: 
    :param local_parameter: 
    :return: 
    """
    # Constants per system modification
    data_path = local_data_path
    file_extension = 'grb'

    data_file = '%s%d/%s_%d_%02d_era5.%s' % (
        data_path, local_year, local_parameter, local_year, local_month, file_extension)

    if not os.path.isfile(data_file):
        raise Exception(data_file + ' does not exist')

    ds = xarray.open_dataset(data_file)
    return ds


def _get_parameters():
    """

    :return: {list}
    """
    parameters = ['2m_dewpoint_temperature',
                  '10m_v_component_of_wind',
                  '10m_u_component_of_wind',
                  'cloud_base_height',
                  'snow_depth',
                  'soil_temperature_level_4',
                  'surface_pressure',
                  'surface_solar_radiation_downwards',
                  'surface_thermal_radiation_downwards',
                  'total_cloud_cover',
                  'total_precipitation',
                  'total_sky_direct_solar_radiation_at_surface'
                  ]
    return parameters


def preprocess(d_year, d_data_path):
    city_list = _get_city_coordinates()
    for d_month in range(2, 13):
        data_sets = []
        try:
            print('Processing files for %d-%d in %s' % (d_year, d_month, data_path))
            for parameter in _get_parameters():
                data_sets.append(_get_netcdf_to_process(d_year, d_month, parameter, d_data_path))

            count = 0
            for city in city_list.itertuples():
                if count % 1000 == 0:
                    print('Processed %s cities so far [%s]' % (count, datetime.datetime.now()))
                city_by_month_ds = _merge_by_city(city, data_sets)
                output_folder = '%s%s/%s/' % (d_data_path, 'processed', d_year)

                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                full_path = output_folder + _get_file_name(d_year, d_month, city.iso3, city.city.lower())

                city_by_month_ds.to_netcdf(full_path, mode='w', compute=True)
                count = count + 1
        finally:
            for data_set in data_sets:
                data_set.close()


def _merge_by_city(city, data_sets):
    all_variables = []
    for data_set in data_sets:
        one_variable_ds = data_set.sel(latitude=city.lat, longitude=city.lon % 360, method='nearest').drop(
            ['longitude', 'latitude'])
        all_variables.append(one_variable_ds)

    return xarray.merge(all_variables)


def _get_file_name(local_year, local_month, iso3, city):
    file_name = '%d-%02d-%s_%s.nc' % (local_year, local_month, iso3, city)
    file_name = file_name.replace(' ', '_').lower()
    return file_name


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pre-process files for year-month combination')
    parser.add_argument('year', type=int, help='an integer representing the year, e.g., 2017')
    parser.add_argument('path', help='a string indicating the system path leading to where the data is. '
                                     'e.g., data/')

    args = parser.parse_args()
    year = args.year
    data_path = args.path
    preprocess(year, data_path)
