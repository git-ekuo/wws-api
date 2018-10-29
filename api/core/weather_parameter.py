"""
A simple parameter class to guard all knowledge about the parameters processed by this weather API
"""


class WeatherParameter:

    @staticmethod
    def get_all_parameters():
        """
        This returns a list of parameters currently supported for analysis

        :return: List[str]
        """
        return ['2m_dewpoint_temperature',
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
