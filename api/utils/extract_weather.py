import os
import time
from datetime import datetime as dt, timedelta

import pandas as pd
import xarray as xr


def get_weather(year, month, lat, lon, tz):
    """

    :param year:
    :param month:
    :param lat:
    :param lon:
    :param tz:
    :return:
    """
    data_path = 'data/'

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

    paramter_dict = {
        '2m_dewpoint_temperature': 'd2m',
        '10m_v_component_of_wind': 'v10',
        '10m_u_component_of_wind': 'u10',
        'cloud_base_height': 'cbh',
        'snow_depth': 'sd',
        'soil_temperature_level_4': 'stl4',
        'surface_pressure': 'sp',
        'surface_solar_radiation_downwards': 'ssrd',
        'surface_thermal_radiation_downwards': 'strd',
        'total_cloud_cover': 'tcc',
        'total_precipitation': 'tp',
        'total_sky_direct_solar_radiation_at_surface': 'fdir'
    }

    # Dataframe to return extracted parameter values
    df = pd.DataFrame()

    if tz < 0:
        start, end = dt(year=year, month=month, day=1), dt(year=year, month=month, day=1) + timedelta(days=40)
    else:
        start, end = dt(year=year, month=month, day=1) - timedelta(days=1), dt(year=year, month=month, day=1)
    for d in [start]:
        # master_ds = xr.Dataset()
        master_array = []

        for parameter in parameters:
            data_file = '%s%d/%s_%d_%02d_era5.nc' % (data_path, d.year, parameter, d.year, d.month)
            print(data_file)
            if os.path.isfile(data_file) and os.path.getsize(data_file) > 1e8:
                ds = xr.open_dataset(data_file)

                ds2 = ds.sel(latitude=lat, longitude=lon % 360, method='nearest').drop(['longitude', 'latitude'])
                master_array.append(ds2)
                # print(timeit(ds2.load))

        # print('master array')
        result_ds = xr.merge(master_array)
        print(result_ds)
        df = result_ds.to_dataframe()
    #
    # # Simple conversion of parameters
    # df['ssrd'] = (df['ssrd'] / 3600).astype(int)  # Convert from J/m^2 to W/m^2
    # df['strd'] = (df['strd'] / 3600).astype(int)
    # df['fdir'] = df['fdir'].fillna(0)
    # df['fdir'] = (df['fdir'] / 3600).astype(int)
    # df['d2m'] = (df['d2m'] - 273.15).round(2)  # Convert from K to C
    # df['t2m'] = (df['t2m'] - 273.15).round(2)  # Convert from K to C
    # df['stl4'] = (df['stl4'] - 273.15).round(2)  # Convert from K to C
    # df['tcc'] = (df['tcc'] * 10).astype(int)  # Total Cloud Cover in tenth
    # df['opaqueCC'] = df['tcc']
    # df['sp'] = df['sp'].astype(int)
    # # Convert from kg of water equivalent to cm (https://confluence.ecmwf.int/display/TIGGE/Snow+depth+water+equivalent)
    # df['sd'] = (df['sd'] * 10 * 5).round(1)
    # # Note that this is an approximation, should check another parameter (GRIB)
    # df['cbh'] = df['cbh'].fillna(-1).astype(int)  # Round to whole numbers (cloud base height)
    #
    # # Parameters that are not currently used by EnergyPlus or I haven't calculated them yet
    # df['Visibility'] = 9999
    # df['PrecipH2O'] = 999
    # df['AerosolDepth'] = 0.999
    # df['DaysSinceSnow'] = 99
    # df['LiquidHours'] = 0
    #
    # # Adjust time to local (from GMT - note no daylight savings)
    # df.index = df.index + timedelta(hours=tz)
    #
    # # Select only the applicable months
    # df = df[df.index.month == month]
    #
    # # Drop unnecessary columns
    # df = df.drop(['latitude', 'longitude', 'time', 'temp', 'u10', 'v10', 'airmass'], axis=1)

    return df


def extract_weather():
    return time_fn(get_weather, year=2012, month=1, lon=-120.496245, lat=50.010341, tz=-1)


def time_fn(fn, *args, **kwargs):
    start = time.process_time()
    start_process = time.perf_counter()
    results = fn(*args, **kwargs)
    end = time.process_time()
    end_process = time.perf_counter()
    fn_name = fn.__module__ + "." + fn.__name__
    print("Process time for " + fn_name + ": " + str(end - start) + "s")
    print("Total time for " + fn_name + ": " + str(end_process - start_process) + "s")
    return results


data_frame = extract_weather()
print(data_frame.describe())
