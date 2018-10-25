import pandas as pd
import os
import xarray
import argparse
import time


def _get_city(city_name):
    """

    :return:
    """
    city_list = pd.read_csv(os.path.join('data', 'simplemaps-worldcities-basic.csv'))
    city_list = city_list.sort_values('lat', ascending=True)
    city_list = city_list.sort_values('lng', ascending=True)
    city_list = city_list.rename(columns={'lat': 'lat', 'lng': 'lon'})
    cities = city_list.loc[city_list["city"] == city_name]
    if cities.empty:
        raise Exception('Cannot find your city')

    for city in cities.itertuples():
        return city

def _get_data_set(local_year, local_month, city_name, local_data_path):
    """

    :param local_year:
    :param local_month:
    :param city_name:
    :param local_data_path:
    :return:
    """
    local_city = _get_city(city_name)
    file_name = _get_file_name(local_year, local_month, local_city.iso3, local_city.city)
    full_path = '%sprocessed/%s/%s' % (local_data_path, local_year, file_name)

    if not os.path.isfile(full_path):
        raise Exception(full_path + 'does not exist')

    ds = xarray.open_dataset(full_path)
    return ds


def get_weather(local_year, local_month, local_city, local_data_path):
    return _get_data_set(local_year, local_month, local_city, local_data_path)


def _get_file_name(local_year, local_month, iso3, city):
    file_name = '%d-%02d-%s_%s.nc' % (local_year, local_month, iso3, city)
    file_name = file_name.replace(' ', '_').lower()
    return file_name


def time_fn(fn, *args, **kwargs):
    start_process = time.perf_counter()
    results = fn(*args, **kwargs)
    end_process = time.perf_counter()
    print("in " + str(end_process - start_process) + "s")
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read pre-processed weather files for a city-year-month combination')
    parser.add_argument('year', type=int, help='an integer representing the year, e.g., 2017')
    parser.add_argument('month', type=int, help='an integer representing the month, e.g., 2')
    parser.add_argument('city', help='city name')
    parser.add_argument('path', help='a string indicating the system path leading to where the data is. '
                                     'e.g., data/')

    args = parser.parse_args()
    year = args.year
    month = args.month
    city = args.city
    data_path = args.path
    ds = get_weather(year, month, city, data_path)
    print(ds)
