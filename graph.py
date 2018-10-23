"""
This class takes any responsibility in creation of a graph.
"""
import numpy as np
import pandas as pd
import xarray as xr
from climate_data import fetch_city_by_name

# Constants
year = 2017  # We are always looking at data from 2017


def create_electricity_consumption_graph(city_name, elec_use):
    lat, lon, city_name = fetch_city_by_name(city_name)

    color_capacity = 0.7
    color_border_capacity = 1.0

    winter_t, summer_t, ave_t = get_subset(year, lat, lon)

    elec_min = elec_use[0]
    elec_max = elec_use[1]
    elec_base, elec_hvac = calculate_electricity(ave_t, elec_min, elec_max)

    return {
        'data': [{'x': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                  'y': elec_base,
                  'type': 'bar',
                  'name': 'baseline',
                  'marker': dict(
                      color='rgba(204, 204, 204, %s)' % color_capacity,
                      line=dict(
                          color='rgba(204, 204, 204, %s)' % color_border_capacity,
                          width=1
                      ))},
                 {'x': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                  'y': elec_hvac,
                  'type': 'bar',
                  'name': '$ on cooling',
                  'marker': dict(
                      color='rgba(255, 94, 91, %s)' % color_capacity,
                      line=dict(
                          color='rgba(255, 94, 91, %s)' % color_border_capacity,
                          width=1,
                      )
                  )
                  }
                 ],
        'layout': {
            'height': 300,
            'barmode': 'stack',
            'legend': {'orientation': 'v', 'xanchor': 'right', 'yanchor': 'top'},
            'margin': dict(l=30, r=30, t=30, b=30, pad=5),
            'yaxis': {'range': [0, elec_max + 20],
                      'tickprefix': '$', 'automargin': True
                      },
        }
    }


def get_subset(year, lat, lon):
    """
    Function to get monthly average temperature with global coverage (0.25 x 0.25)
    Source: ECMWF ERA5 dataset
    Input: get_subset(year,lat,lon)

    :param year:
    :param lat:
    :param lon:
    :return:
    """

    # Get daily average temperature
    t2 = xr.open_dataset('data/T2_monthly_mean_2017.nc')
    average_temp = t2.sel(lat=lat, lon=lon % 360, method='nearest')
    average_temp = average_temp.assign_coords(
        time=(pd.to_datetime(np.array(average_temp.time).astype(int).astype(str))))

    return None, None, average_temp.var167


def calculate_electricity(average_temp, electricity_bill_min, electricity_bill_max):
    """
    Given the daily average temperature data, minimum and maximum an user pay for her power bill, we can work out
    the baseline, and also the amount she is paying for cooling

    :param average_temp:
    :param electricity_bill_min:
    :param electricity_bill_max:
    :return: a pair of array: base line electricity that user pays, and electricity user pays for cooling.
        They are grouped at the monthly level
    """
    average_temp = average_temp - 273.15
    cooling_degree_day = average_temp.where(average_temp > 18, 18) - 18
    monthly_cdd = cooling_degree_day

    elec_base = electricity_bill_min * np.ones(12)
    elec_hvac = np.array(monthly_cdd * (electricity_bill_max - electricity_bill_min) / max(monthly_cdd))

    return elec_base, elec_hvac
