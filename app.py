# Import required libraries
import os
# Web-related
import traceback

import boto3
import botocore
import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
# Numerical stuff
import pandas as pd
import xarray
import xarray as xr
from dash.dependencies import Input, Output
from flask import request, json, send_file

# OikoLab internal import
from intent import handle_intent_request


def _get_city_options():
    city_list = pd.read_csv(os.path.join('data', 'simplemaps-worldcities-basic.csv'))
    city_list = city_list.sort_values('pop', ascending=False)
    city_list['loc'] = city_list['city'] + ', ' + city_list['country']
    city_list = city_list.rename(columns={'lat': 'Lat', 'lng': 'Lon'})
    city_options = [{'label': city, 'value': index} for city, index in zip(city_list['loc'], city_list.index)]
    return city_options


def construct_app():
    app = dash.Dash(__name__, assets_folder='assets', static_folder='assets')  # static url path is 'assets' by default
    app.css.append_css({'external_url': 'https://fonts.googleapis.com/css?family=Open+Sans|Roboto'})

    app.title = 'OikoLab'
    app.layout = html.Div(
        # Controls
        children=[
            dcc.Markdown(
'''
# OikoLab

## A simple, fast access to ERA5 reanalysis data
---
'''
            ),
            html.Div(
                className='four columns container-input',
                children=[html.Div(
                    children=[
                        html.Div(id='latlon_dropdown_text',
                                 style={'display': 'block',
                                        'margin-bottom': '20px'},
                                 children='City'),
                        dcc.Dropdown(id='latlon_dropdown',
                                     options=_get_city_options(),
                                     placeholder='Select a city',
                                     value=''
                                     )
                    ]
                ),
                ]

            )
            ,
            # Charts based on the controls
            html.Div(
                id='section-chart',
                # Fix the height, because dash charts height is weirdly large when there is no data.
                style={'height': '376px'},
                className='eight columns',
                children=[
                    html.Div(
                        children=[
                            html.Div(style={'margin-bottom': '40px'},
                                     children=[dcc.Graph(id='elec_usage', config={'displayModeBar': False})],
                                     )
                        ]
                    )
                ]
            )
        ]
    )
    return app


app = construct_app()
server = app.server


def get_subset(lat, lon):
    """
    Function to get monthly average temperature with global coverage (0.25 x 0.25)
    Source: ECMWF ERA5 dataset
    Input: get_subset(year,lat,lon)

    :param lat:
    :param lon:
    :return:
    """

    # Get daily average temperature
    T2 = xr.open_dataset('data/T2_monthly_mean_2017.nc')
    average_temp = T2.sel(lat=lat, lon=lon % 360, method='nearest')
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
    elec_HVAC = np.array(monthly_cdd * (electricity_bill_max - electricity_bill_min) / max(monthly_cdd))

    return elec_base, elec_HVAC


@app.callback(Output(component_id='elec_usage', component_property='figure'),
              [Input(component_id='latlon_dropdown', component_property='value')])
def update_elec(location):
    city_list = _get_city_options()
    if location:
        lat = city_list.loc[location]['Lat']
        lon = city_list.loc[location]['Lon']
    else:
        lat = 42.36
        lon = -71.06
    if location:
        lat = city_list.loc[location]['Lat']
        lon = city_list.loc[location]['Lon']
        color_capacity = 0.7
        color_border_capacity = 1.0
    else:
        lat = 42.36
        lon = -71.06
        color_capacity = 0.05
        color_border_capacity = 0.05

    winterT, summerT, aveT = get_subset(lat, lon)

    elec_min = 100
    elec_max = 150
    elec_base, elec_HVAC = calculate_electricity(aveT, elec_min, elec_max)

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
                  'y': elec_HVAC,
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


"""
REST API SECTION
"""


@app.callback(
    dash.dependencies.Output('section-chart', 'style'),
    [Input(component_id='latlon_dropdown', component_property='value')])
def show_chart(location):
    if location:
        return {'visibility': 'visible', 'height': '376px', 'overflow': 'auto'}
    else:
        return {'visibility': 'visible', 'height': '376px', 'overflow': 'auto'}


@app.server.route('/intent', methods=['POST'])
def intent():
    """
    :return: string: response with Dialogflow response structure
    """
    print("Request: %s" % json.dumps(request.json))
    response = ''
    try:
        response = handle_intent_request(request=request)
        print("Response: %s" % response)
    except Exception:
        app.server.logger.error("An exception occurred")
        traceback.print_exc()

    return response


@app.server.route('/weather', methods=['GET'])
def read_weather():
    """

    :return:
    """
    year = request.args.get('y')
    city_name = request.args.get('city')

    if year is None or city_name is None:
        return 'Please specify the year and the city: e.g., "?y=2017&city=new york"'

    if str(year) != '2017':
        return 'Only 2017 is supported for now'

    # check city
    checked_city = _get_city(city_name)
    if checked_city is None:
        return 'Cannot determine your city'

    bucket = 'ec2-us-east-1-oikolab'
    client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                          config=botocore.client.Config(signature_version=botocore.UNSIGNED))

    prefix = 'processed/%s/' % year

    data_sets = []
    for month in range(1, 13):
        metadata_file = _get_file_name(2017, month, checked_city.iso3, checked_city.city)
        metadata_key = prefix + metadata_file
        print('metadata_key: ' + metadata_key)
        client.download_file(bucket, metadata_key, metadata_file)
        data_sets.append(xarray.open_dataset(metadata_file, decode_times=False))

    final_ds = xarray.concat(data_sets, dim='time')
    full_path = '/tmp/weather_temp_storage.nc'
    final_ds.to_netcdf(full_path, mode='w', compute=True)
    print(final_ds)
    return send_file(full_path, as_attachment=True,
                     attachment_filename=_get_download_file_name(2017, checked_city.iso3, checked_city.city))


def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join('./', filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src, 'rb').read()
    except IOError as exc:
        return str(exc)


def _get_city(city_name):
    """

    :return:
    """
    city_list = pd.read_csv(os.path.join('data', 'simplemaps-worldcities-basic.csv'))
    city_list = city_list.sort_values('lat', ascending=True)
    city_list = city_list.sort_values('lng', ascending=True)
    city_list = city_list.rename(columns={'lat': 'lat', 'lng': 'lon'})
    cities = city_list.loc[city_list["city"] == city_name.title()]
    if not cities.empty:
        for city in cities.itertuples():
            return city

    provinces = city_list.loc[city_list["province"] == city_name]
    if not provinces.empty:
        for province in provinces.itertuples():
            return province

    return None


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


def _get_download_file_name(local_year, iso3, city):
    file_name = '%d-%s_%s.nc' % (local_year, iso3, city)
    file_name = file_name.replace(' ', '_').lower()
    return file_name


# Main
if __name__ == '__main__':
    app.server.run(threaded=True)
