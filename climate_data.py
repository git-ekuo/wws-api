import os

import pandas as pd
from geopy.distance import geodesic
from geopy.geocoders import Nominatim


def get_climate(city_name):
    """
    get climate data (closest EPW weather file) based on city location
    City location based on about 7000 cities in the world (https://simplemaps.com/data/world-cities) or Nominatim()

    :param city_name:
    :return:
    """
    geolocator = Nominatim(user_agent="home-energy")

    lat, lon, city = fetch_city_by_name(city_name)
    if lat is None:
        # Note that this option tends to be quite slow (~1.5s), so reserved for cases when city name can't be found.
        location = geolocator.geocode(city_name, addressdetails=True)
        lat, lon = location.latitude, location.longitude
        city = location.raw['address']['city']

    df = pd.read_csv('epwlist.csv')
    df['Distance'] = df.apply(lambda x: geodesic((x['lat'], x['lon']), (lat, lon)).kilometers, axis=1)
    ID = df['Distance'].idxmin()

    return df.loc[ID], city


def fetch_city_by_name(city_name):
    """
    This fetches from the stored data, returns the info on city if it can be found on our data source.

    :param city_name: string:
    :return:
    """
    cities = pd.read_csv(os.path.join('data', 'simplemaps-worldcities-basic.csv'))
    cities['loc'] = cities['city'] + ', ' + cities['country']
    cities = cities.sort_values('pop', ascending=False)
    lat, lon, city = None, None, None

    if city_name in cities['city'].values:
        city_in_csv = cities[cities['city'] == city_name]
        if len(city_in_csv['lat'].values) == 1:
            lat, lon = float(city_in_csv['lat'].values), float(
                city_in_csv['lng'].values)

        else:  # use the first one, if multiple are found
            lat, lon = float(city_in_csv['lat'].values[0]), float(
                city_in_csv['lng'].values[0])

        city = city_name

    return lat, lon, city


def get_monthly_ave_T(lat, lon, month):
    """
    0.5 x 0.5 reanalysis downloaded from
    # https://www.esrl.noaa.gov/psd/data/gridded/data.ghcncams.html

    :param lat:
    :param lon:
    :param month:
    :return:
    """
    import xarray as xr

    # Index of previous month
    months = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    prev_month = months[month - 1]

    monthly = xr.open_dataset('data/air.mon.mean.nc')
    subset = monthly.sel(lat=lat, lon=lon % 360, method='nearest').air

    subset = subset.sel(time=slice('2018', '2019'))
    subset = subset.where(subset.time.dt.month == prev_month, drop=True)

    return float(subset.values - 273.15)


def chat_about_city(climate, city, temp_unit):
    import datetime
    from dateutil.relativedelta import relativedelta

    now = datetime.datetime.now()

    if temp_unit == 'F':
        design_heating_T = int(climate['design_heating_T'] * 1.8 + 32)
        design_cooling_T = int(climate['design_cooling_T'] * 1.8 + 32)

    else:
        design_heating_T = int(climate['design_heating_T'])
        design_cooling_T = int(climate['design_cooling_T'])

    chat = {}

    if climate['ClimateZone'] == '0A/B - extremely hot':
        chat['winter'] = None
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '1A/B - very hot':
        chat['winter'] = None
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '2A/B - hot':
        chat['winter'] = None
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '3A/B - warm':
        chat['winter'] = 'Winter design temperature is about %d%s.' % (design_heating_T, temp_unit)
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '3C - warm marine':
        chat['winter'] = 'Winter design temperature is about %d%s.' % (design_heating_T, temp_unit)
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '4A/B - mixed':
        chat['winter'] = 'Winter design temperature is about %d%s.' % (design_heating_T, temp_unit)
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '4C - mixed marine':
        chat['winter'] = 'Winter design temperature is about %d%s.' % (design_heating_T, temp_unit)
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '5A/B - cool':
        chat['winter'] = 'Winter design temperature is about %d%s.' % (design_heating_T, temp_unit)
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '5C - cool marine':
        chat['winter'] = 'Winter design temperature is about %d%s.' % (design_heating_T, temp_unit)
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '6A/B - cold':
        chat['winter'] = 'Winter design temperature is about %d%s.' % (design_heating_T, temp_unit)
        chat['summer'] = 'Summer design temperature is about %d%s.' % (design_cooling_T, temp_unit)

    elif climate['ClimateZone'] == '7 - very cold':
        chat['winter'] = 'Winter design temperature is about %d%s.' % (design_heating_T, temp_unit)
        chat['summer'] = None

    elif climate['ClimateZone'] == '8 - subarctic/arctic':
        chat['winter'] = 'Winter design temperature is about %d%s.' % (design_heating_T, temp_unit)
        chat['summer'] = None

    recent_average = get_monthly_ave_T(climate['lat'], climate['lon'], now.month)

    ave_diff = recent_average - climate[str(now.month - 1)]
    last_month = now - (relativedelta(months=1))

    # Generate comparison for the past data
    if ave_diff > 2:
        comment = 'The past month has been unusually warmer than the average %s.' % last_month.strftime("%B")
    elif ave_diff > 1 and ave_diff <= 2:
        comment = 'The past month has been somewhat warmer than the average %s.' % last_month.strftime("%B")
    elif ave_diff <= 1 and ave_diff >= -1:
        comment = 'The past month has been typical of the average %s.' % last_month.strftime("%B")
    elif ave_diff < -1 and ave_diff >= -2:
        comment = 'The past month has been somewhat colder than the average %s.' % last_month.strftime("%B")
    else:  # ave_diff < -2
        comment = 'The past month has been unusually colder than the average %s.' % last_month.strftime("%B")

    chat['general'] = 'Ah %s! FYI, the climate zone is %s. %s' % (city, climate['ClimateZone'], comment)

    return chat
