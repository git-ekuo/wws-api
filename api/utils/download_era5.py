"""
This file downloads the 22 variables from ECMWF ERA5 reanalysis in `parameters` variable, and store them under `data_path`.

File `.cdsapirc` must be set up with a key and a URL: https://cds.climate.copernicus.eu/api/v2.
The size of ERA5 dataset is huge, it's expected that it's downloaded to a cheap storage.
"""
import cdsapi
import os

c = cdsapi.Client()

parameters = ['2m_dewpoint_temperature',
              '2m_temperature',
              '10m_v_component_of_wind',
              '10m_u_component_of_wind',
              'cloud_base_height',
              'snow_depth',
              'snowfall',
              'snow_density',
              'soil_temperature_level_1',
              'soil_temperature_level_2',
              'soil_temperature_level_3',
              'soil_temperature_level_4',
              'surface_pressure',
              'downward_uv_radiation_at_the_surface',
              'surface_solar_radiation_downwards',
              'surface_thermal_radiation_downwards',
              'total_cloud_cover',
              'total_precipitation',
              'total_column_rain_water',
              'total_sky_direct_solar_radiation_at_surface',
              'total_column_water_vapour',
              'forecast_albedo'
              ]

data_path = 's3bucket'

for y in [2016, 2015, 2014, 2013, 2012]:
    directory = "/%s/%s" % (data_path, str(y))

    for m in range(1, 13):
        for parameter in parameters:
            filename = '%s_%d_%02d_era5.grb' % (parameter, y, m)
            try:

                if not os.path.exists(directory):
                    os.makedirs(directory)

                file_list = [file for file in os.listdir(directory) if file.endswith('.grb')]

                if filename not in file_list:
                    print('year: %d month:%d' % (y, m))

                    c.retrieve(
                        'reanalysis-era5-single-levels',
                        {
                            'variable': parameter,
                            'product_type': 'reanalysis',
                            'year': str(y),
                            'month': ['%02d' % m],
                            'day': [
                                '01', '02', '03',
                                '04', '05', '06',
                                '07', '08', '09',
                                '10', '11', '12',
                                '13', '14', '15',
                                '16', '17', '18',
                                '19', '20', '21',
                                '22', '23', '24',
                                '25', '26', '27',
                                '28', '29', '30',
                                '31'
                            ],
                            'time': [
                                '00:00', '01:00', '02:00',
                                '03:00', '04:00', '05:00',
                                '06:00', '07:00', '08:00',
                                '09:00', '10:00', '11:00',
                                '12:00', '13:00', '14:00',
                                '15:00', '16:00', '17:00',
                                '18:00', '19:00', '20:00',
                                '21:00', '22:00', '23:00'
                            ],
                            'format': 'netcdf'
                        },
                        os.path.join(directory, filename)
                    )
            except:
                print('Error in getting %s' % filename)
