"""
This module acts as a `service` that analyses requests from chat bot and have them handled with the most
appropriate response.
"""
import os
import time

import plotly.graph_objs as go
import plotly.io as pio
from flask import json, url_for

from climate_data import get_climate, chat_about_city, fetch_city_by_name
from graph import create_electricity_consumption_graph


def handle_intent_request(request):
    """
    Generic service method to handle all intent queries (HTTP POST requests) from DialogFlow

    :param request:
    :return: json
    """
    query_result = request.json["queryResult"]
    if 'intent' not in query_result:
        return __no_answer_response(request)

    identified_intent = query_result['intent']['displayName']

    if 'Bill inquiry - address' == identified_intent:
        return handle_address_inquiry(request)
    elif 'Bill inquiry - address - bill' == identified_intent:
        return handle_address_billing_inquiry(request)
    elif 'Bill inquiry - address - bill - more' == identified_intent:
        return handle_address_billing_more_inquiry(request)
    elif 'Product inquiry' == identified_intent:
        return handle_product_inquiry(request)
    return __no_answer_response(request)


def handle_address_inquiry(request):
    """
    This focuses on handling inquiries when we only have address information.
    It returns something informational about the city where user stays

    :param request:
    :return: json
    """
    parameters = request.json["queryResult"]['parameters']
    if 'geo-city' not in parameters:
        return __no_answer_response(request)

    city = parameters['geo-city']

    (climate, city) = get_climate(city)
    chat_response_dict = chat_about_city(climate=climate, city=city, temp_unit='F')
    desc_on_city = chat_response_dict['general']
    next_question = 'Can you tell me roughly the minimum amount you paid for your electricity? e.g., \"$160\"'
    text_array = [desc_on_city, next_question]

    return __construct_rich_text_response(text_array)


def handle_address_billing_inquiry(request):
    """
    This focuses on handling inquiries when address information and user billing info
    are available, it returns usage analysis of the user in the past month.

    :param request:
    :return: json
    """
    context_array = request.json["queryResult"]['outputContexts']
    parameters = dict()
    for context in context_array:
        context_parameters = context['parameters']
        if 'contexts/generic' in context['name']:
            parameters['bill-high'] = context_parameters['bill-high'][0]
            parameters['bill-low'] = context_parameters['bill-low'][0]
            parameters['city'] = context_parameters['geo-city']

    city_name = parameters['city']
    lat, lon, city_name = fetch_city_by_name(city_name)

    figure_dict = create_electricity_consumption_graph(city_name, [parameters['bill-low'], parameters['bill-high']])
    figure = go.Figure(figure_dict)

    if not os.path.exists('assets'):
        os.mkdir('assets')
    current_time = int(time.time())
    file_name = '%s-%s.png' % (city_name, current_time)
    pio.write_image(figure, 'assets/%s' % file_name)

    image_uri = url_for('static', filename=file_name, _external=True)

    source = __detect_source(request)
    response = __create_empty_rich_response()
    __add_image_to_response(response, image_uri, source)
    __add_text_to_response(response, "Got it! This is what we know about your consumption!", source)
    __add_text_to_response(response,
                           "Based on our analysis of weather data and your property data, your bill is still looking ok! The amount you are paying is still reasonable in comparison to others living at similar sized houses.",
                           source)

    return json.dumps(response)


def handle_address_billing_more_inquiry(request):
    """
    This focuses on handling inquiries when address information and user billing info
    are available, it returns usage analysis of the user in the past month.

    :param request:
    :return: json
    """
    context_array = request.json["queryResult"]['outputContexts']
    parameters = dict()
    for context in context_array:
        context_parameters = context['parameters']
        if 'contexts/generic' in context['name']:
            parameters['bill-high'] = context_parameters['bill-high']['amount']
            parameters['bill-low'] = context_parameters['bill-low']['amount']
            parameters['city'] = context_parameters['geo-city']

    text_messages = ["Based on forecast, it's looking to be hotter, please make sure your AC is in good working order",
                     "Just a tip! Close your curtain during the day, it will help to keep the heat from getting into your house, so it's easier to cool at night."]

    return __construct_rich_text_response(text_messages)


def __construct_rich_text_response(text_array):
    """
    Returns a rich message with multiple lines of texts

    :param text_array:
    :return: json
    """
    text_messages = "\n\n".join(text_array)

    response_message = {
        "fulfillmentText": text_messages
    }
    return json.dumps(response_message)


def __construct_image_response(image_uri, text_array):
    """
    Private method to create a simple image response.

    :param image_uri: string:
    :return: json formatted string, for DialogFlow
    """
    text_messages = "\n\n".join(text_array)

    response = {
        "fulfillmentMessages": [
            {
                "image": {
                    "imageUri": image_uri,
                    "text": text_messages
                }
            }
        ]
    }
    return json.dumps(response)


def __construct_single_card_response(title, text_array, image_uri):
    """
    Private method to construct a single card as its response

    :param text_array: string: title of one card
    :param image_uri: string: absolute URL of an image
    :return: string: json formatted string, that is ready to be sent back to Dialogflow
    """

    title = title
    subtitle = "\n\n".join(text_array)

    response = {"fulfillmentMessages": [
        {
            "card": {
                "title": title,
                "subtitle": subtitle,
                "imageUri": image_uri,
            }
        }]}
    return json.dumps(response)


def __detect_source(request):
    try:
        source = request.json['originalDetectIntentRequest']['source']
        if "slack" in source:
            return "SLACK"
        else:
            return "FACEBOOK"
    except KeyError:
        pass

    return 'unknown'


def __no_answer_response(request):
    """
    For returning a simple text response for requests that we fail to answer, for different reasons.

    :return: string
    """
    original_response = {
        "fulfillmentText": request.json["queryResult"]["fulfillmentText"],
        "fulfillmentMessages": request.json["queryResult"]["fulfillmentMessages"],
        "source": request.json["originalDetectIntentRequest"]["source"],
        "payload": request.json["originalDetectIntentRequest"]["payload"]
    }
    try:
        original_response["outputContext"] = request.json["queryResult"]["outputContexts"]
        original_response["followupEventInput"] = request.json["queryResult"]["followupEventInput"]
    except KeyError:
        pass

    return json.dumps(original_response)


def __add_image_to_response(response, image_uri, platform):
    image_body = {
        "image": {
            "imageUri": image_uri
        },
        "platform": platform
    }
    response['fulfillmentMessages'].append(image_body)
    return response


def __add_text_to_response(response, text, platform):
    text_body = {
        "text": {
            "text": [text]
        },
        "platform": platform
    }
    response['fulfillmentMessages'].append(text_body)
    return response


def __create_empty_rich_response():
    response = {
        "fulfillmentMessages": []
    }
    return response


def __create_facebook_carousel_response(element_array):
    response = {
        "payload": {
            "facebook": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": element_array
                    }
                }
            }
        }
    }
    return response


def handle_product_inquiry(request):
    """
    This handles the initial product inquiry by a user.
 
    :param request:
    :return:string
    """""
    element_array = []

    __append_facebook_carousel_item(element_array=element_array, title='Low-E window film', description='123',
                                    image_uri="http://www.prosmartsolarsolutions.com/wp-content/uploads/2017/06/solar-film-block.jpg")
    __append_facebook_carousel_item(element_array=element_array, title='Double glazing window', description='123',
                                    image_uri="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR229VHak-AivSGFJXTujz6WnddoYP78gET26lq-cLdaPNpg86iDQ")
    __append_facebook_carousel_item(element_array=element_array, title='DIY window insulation',
                                    description='DIY window insulation',
                                    image_uri="https://diy.sndimg.com/content/dam/images/diy/fullset/2016/Jan/9/0/Original_Emily-Fazio_insulating-home-during-winter_tightening-insulation-plastic.jpg.rend.hgtvcom.1280.960.suffix/1452352444745.jpeg")
    __append_facebook_carousel_item(element_array=element_array, title='Curtain and blinds',
                                    description='Curtain and blinds',
                                    image_uri="http://www.lagueltee.com/pic/Curtain-Outstanding-Curtains-With-Blinds-Blinds-And-Curtains-Together-Ideas-Curtains-And.jpg")
    response = __create_facebook_carousel_response(element_array)
    return json.dumps(response)


def __append_facebook_carousel_item(element_array, title, description, image_uri):
    payload = "tell me more about %s" % title
    carousel_item = {
        "title": title,
        "image_url": image_uri,
        "subtitle": description,
        "buttons": [
            {
                "type": "postback",
                "title": "Tell me more",
                "payload": payload
            }
        ]
    }
    element_array.append(carousel_item)
    return element_array
