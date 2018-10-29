"""
A simple CLI to retrieves a weather data set
"""

import argparse

from api.outgest.weather_service import WeatherService

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read pre-processed weather files for a city-year-month combination')
    parser.add_argument('year', type=int, help='an integer representing the year, e.g., 2017')
    parser.add_argument('month', type=int, help='an integer representing the month, e.g., 2')
    parser.add_argument('city', help='city name')
    parser.add_argument('path', help='a string indicating the system path leading to where the data is. '
                                     'e.g., data/')

    # Reads the arguments
    args = parser.parse_args()
    year = args.year
    month = args.month
    city = args.city
    data_path = args.path

    weather_service = WeatherService(data_path)
    weather_ds = weather_service.get_weather_data_set(year, month, city)
    print(weather_ds)
