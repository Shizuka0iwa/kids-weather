import requests
import json
import time
import sqlite3
import pycountry

from sqlite3 import Error
from datetime import datetime, timezone
from requests.models import Response

import constants

def get_output(country, zipcode, from_hour, to_hour, current_hour_utc, lat, lon):

    output = []
    if from_hour <= current_hour_utc <= to_hour:
        # Get historical data from from_hour - 1 of the day
        output = get_history(from_hour, current_hour_utc - 1, lat, lon)
    
        # Get forecast to to_hour of the day
        forecast = get_forecast(0, to_hour - current_hour_utc, lat, lon)
        for i in range(len(forecast)):
            output.append(forecast[i])
    else:
        # Get the forecast for the next day
        if from_hour > current_hour_utc:
            first = from_hour - current_hour_utc
            last = to_hour - current_hour_utc
        else:
            first = from_hour + 24 - current_hour_utc
            last = to_hour + 24 - current_hour_utc
        output = get_forecast(first, last, lat, lon)
    return output


def call_forecast_api(lat, lon):
    try:
        api_key = constants.OpenWeather_API
        current = 'current'
        minutely = 'minutely'
        daily = 'daily'
        alerts = 'alerts'
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={current,minutely,daily,alerts}&units=metric&appid={api_key}"

        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.RequestException:
        return None


def call_history_api(lat, lon):
    """Get forecast data"""
    try:
        api_key = constants.OpenWeather_API
        dt = int(time.time())
        url = f"https://api.openweathermap.org/data/2.5/onecall/timemachine?lat={lat}&lon={lon}&dt={dt}&units=metric&appid={api_key}"

        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.RequestException:
        return None

def parse_response(response, first, last):
    try:
        forecast = response.json()
        hourly = []
        for i in range(first, last+1):
            data = {}
            data['dt_utc'] = time_converter(forecast['hourly'][i]['dt'])
            data['feels_like'] = forecast['hourly'][i]['feels_like']
            data['weather'] = forecast['hourly'][i]['weather'][0]['id']
            hourly.append(data)
        return hourly

    except (KeyError, TypeError, ValueError):
        return None


def get_forecast(first, last, lat, lon):
    """Get forecast data"""
    response = call_forecast_api(lat, lon)
    return parse_response(response, first, last)


def get_history(first, last, lat, lon):
    """Get forecast data"""
    response = call_history_api(lat, lon)
    return parse_response(response, first, last)


def time_converter(unix_time):
    """Convert Unix time to visible date in UTC."""
    ts = int(unix_time)
    dt_usc = {}
    dt_usc['date'] = int(datetime.utcfromtimestamp(ts).strftime('%d'))
    dt_usc['hour'] = int(datetime.utcfromtimestamp(ts).strftime('%H'))
    return dt_usc


def display_time(hour_24):
    if hour_24 > 12:
        hour_12 = hour_24 - 12
        display_time = str(hour_12) + " p.m."
    else:
        display_time = str(hour_24) + " a.m."
    return display_time


def select_clothes(feels_likes):
    min_feels_like = min(feels_likes)

    clothes = []
    if min_feels_like < 0:
        clothes.append('hat_gloves')
    if min_feels_like < 10:
        clothes.append('worm_jacket')
    if min_feels_like < 15:
        clothes.append('light_jacket')
    if min_feels_like < 20:
        clothes.extend(['long'])
    else:
        clothes.extend(['short'])

    return clothes


def add_items(clothes, weathers):
    if 'snowflake' in weathers:
        clothes.append('snowboots')
    elif any(x in weathers for x in ['cloud-showers-heavy', 'cloud-rain']):
        clothes.append('umbrella')

    return clothes


def database_setup(database):
    conn = create_connection(database)
    db = conn.cursor()
    return db


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    
    return conn


def call_geocoding_api(country, zipcode):
    """Giocoding with zipcode"""
    try:
        api_key = constants.OpenWeather_API
        countrycode = pycountry.countries.get(name=country).alpha_2
        if countrycode == 'CA':
            zipcode = zipcode[0:3]

        url = f"http://api.openweathermap.org/geo/1.0/zip?zip={zipcode},{countrycode}&appid={api_key}"

        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.RequestException:
        return None

def parse_geocode(response):
    try:
        geocode = response.json()
        return geocode

    except (KeyError, TypeError, ValueError):
        return None


def call_geocoding_api(country, zipcode):
    """Giocoding with zipcode"""
    try:
        api_key = constants.OpenWeather_API
        countrycode = pycountry.countries.get(name=country).alpha_2
        if countrycode == 'CA':
            zipcode = zipcode[0:3]

        url = f"http://api.openweathermap.org/geo/1.0/zip?zip={zipcode},{countrycode}&appid={api_key}"

        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.RequestException:
        return None

def parse_geocode(response):
    try:
        geocode = response.json()
        return geocode

    except (KeyError, TypeError, ValueError):
        return None


def is_valid_int(value):

    # Ensure value was numuber
    try:
        num = float(value)
    except ValueError:
        return False

    # Ensure value was int
    try:
        if num.is_integer() == False:
            return False
    except ValueError:
            return False

    # Ensure value is between 0 and 23
    if num < 0 or num >23:
        return False

    return True