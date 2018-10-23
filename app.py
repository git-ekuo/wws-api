# Import required libraries
import os
# Web-related
import traceback

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
# Numerical stuff
import pandas as pd
import xarray as xr
from dash.dependencies import Input, Output
from flask import request, json

# Oiko lab internal import
from intent import handle_intent_request


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
    T2 = xr.open_dataset('data/T2_monthly_mean_2017.nc')
    average_temp = T2.sel(lat=lat, lon=lon % 360, method='nearest')
    average_temp = average_temp.assign_coords(
        time=(pd.to_datetime(np.array(average_temp.time).astype(int).astype(str))))

    return None, None, average_temp.var167


# Get city list
citylist = pd.read_csv(os.path.join('data', 'simplemaps-worldcities-basic.csv'))
citylist = citylist.sort_values('pop', ascending=False)
citylist['loc'] = citylist['city'] + ', ' + citylist['country']
citylist = citylist.rename(columns={'lat': 'Lat', 'lng': 'Lon'})
city_options = [{'label': city, 'value': index} for city, index in zip(citylist['loc'], citylist.index)]

app = dash.Dash(__name__, assets_folder='assets', static_folder='assets')  # static url path is 'assets' by default
app.title = 'Oiko Lab'
server = app.server
year = 2017

# Bootstrap CSS
# Create global chart template & layout
app.css.append_css({'external_url': 'https://fonts.googleapis.com/css?family=Open+Sans|Roboto'})
mapbox_access_token = 'pk.eyJ1Ijoiam9lLW1hZ3BpZXNvbHV0aW9ucy1jbyIsImEiOiJjajdqampocnEyM2tuMzNwZHd2MTdia244In0.fVrkGAPX0qqXzET1x6xL0A'

# Create app layout
app.layout = html.Div(
    # Controls
    children=[
        html.Div(
            className='four columns container-input',
            children=[html.Div(
                children=[
                    html.Div(id='latlon_dropdown_text',
                             style={'display': 'block',
                                    'margin-bottom': '20px'},
                             children='Where do you stay?'),
                    dcc.Dropdown(id='latlon_dropdown',
                                 options=city_options,
                                 placeholder='Your city',
                                 value=''
                                 ),
                    html.Div(
                        children=[html.Div(
                            [html.Div(id='elec_slider_text_question',
                                      children='How much do you pay for power per month?',
                                      style={'display': 'block',
                                             'margin': 'auto',
                                             'margin-top': '40px',
                                             'margin-bottom': '20px',
                                             }),
                             html.Div(
                                 style={'height': '40px'},
                                 children=dcc.RangeSlider(id='elec_slider', min=0, max=300, step=5,
                                                          allowCross=False,
                                                          marks={0: '$0',
                                                                 50: '$50',
                                                                 100: '$100',
                                                                 150: '$150',
                                                                 200: '$200',
                                                                 250: '$250',
                                                                 300: '$300'},
                                                          value=[50, 120])
                             ),
                             html.Div(id='elec_slider_text',
                                      style={'display': 'block',
                                             'margin-bottom': '20px',
                                             'text-align': 'center',
                                             'color': '#999'})]
                        )],
                        style={'height': '120px', 'margin-bottom': '40px'}
                    ),
                    html.Div(id='elec_advice_text',
                             style={'display': 'block',
                                    'margin': 'auto',
                                    'font-size': '2em',
                                    'text-align': 'left'}),
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
              [Input(component_id='latlon_dropdown', component_property='value'),
               Input(component_id='elec_slider', component_property='value')])
def update_elec(location, elec_use):
    if location:
        lat = citylist.loc[location]['Lat']
        lon = citylist.loc[location]['Lon']
    else:
        lat = 42.36
        lon = -71.06
    if location:
        lat = citylist.loc[location]['Lat']
        lon = citylist.loc[location]['Lon']
        color_capacity = 0.7
        color_border_capacity = 1.0
    else:
        lat = 42.36
        lon = -71.06
        color_capacity = 0.05
        color_border_capacity = 0.05

    winterT, summerT, aveT = get_subset(year, lat, lon)

    elec_min = elec_use[0]
    elec_max = elec_use[1]
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


@app.callback(
    dash.dependencies.Output('elec_slider_text', 'children'),
    [dash.dependencies.Input('elec_slider', 'value')])
def update_output(value):
    return '$%d to $%d' % (value[0], value[1])


@app.callback(
    dash.dependencies.Output('elec_advice_text', 'children'),
    [Input(component_id='latlon_dropdown', component_property='value'),
     Input(component_id='elec_slider', component_property='value')])
def update_electricity_advice_text(location, elec_use):
    if location:
        lat = citylist.loc[location]['Lat']
        lon = citylist.loc[location]['Lon']
    else:
        return ''

    winterT, summerT, aveT = get_subset(year, lat, lon)

    elec_min = elec_use[0]
    elec_max = elec_use[1]
    electricity_baseline, electricity_hvac = calculate_electricity(aveT, elec_min, elec_max)
    total_for_hvac = electricity_hvac.sum()

    return 'That\'s roughly $%s for cooling your home' % int(total_for_hvac)


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


# Main
if __name__ == '__main__':
    app.server.run(threaded=True)
