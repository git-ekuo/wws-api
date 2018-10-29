"""
City service that gives access to city information
"""
import pandas as pd
import os


class CityService:

    def __init__(self):
        """Constructor"""
        self.data_path = 'data'
        self.data_file = 'simplemaps-worldcities-basic.csv'

    def get_city_coordinates(self):
        """
        This retrieves the list of major city coordinates
        
        :return: DataFrame
        """
        city_list = pd.read_csv(os.path.join(self.data_path, self.data_file))
        city_list = city_list.sort_values('lat', ascending=True)
        city_list = city_list.sort_values('lng', ascending=True)
        city_list = city_list.rename(columns={'lat': 'lat', 'lng': 'lon'})
        return city_list
