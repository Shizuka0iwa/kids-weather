# Kids Weather

#### Video Demo:  https://youtu.be/-ani6lSOlw4
#### Description:

Kids Weather is a simple weather forecast with icons for little kids who don't read words.

With this app, children can find out the weather and proper clothing for the day.
We don't have to tell them what to wear every morning anymore.

# Fearures
## No texts
It shows weather forecast only with images. Your kids don't need to read any words. Three images tell them the weather in the morning, noon, and evening.

## Suggest what to wear
It shows what to wear for the day based on the feels like temperature. You and your kids don't need to translate the weather forecast to practical ideas such as they need a warm jacket or rain gear.

## Limited time frame
The information is focused on the time when the children are outside, so they won't be confused by irrelevant information such as the rain forecast at midnight or the forecast for the next few days.


# Description
## Feels like temperature >= 20
T-shirt & shorts icons are shown.

## 20 > feels like temperature >= 15
Long sleeve shirt & long pants are shown.

## 15 > feels like temperature >= 10
Sweatshirt, long sleeve shirt & long pants are shown.

## 10 > feels like temperature >= 0
Down jacket, sweatshirt, long sleeve shirt & long pants are shown.

## 0 > feels like temperature
Hat, mittens, down jacket, sweatshirt, long sleeve shirt & long pants are shown.
    

# Prerequisite

- Python 3
- pip
- Openweather API
Follow the instruction about [creating constants.py file](##constants.py).

# Installation

## pip
To set up development emvironment, [follow a instruction and install pip](https://pip.pypa.io/en/stable/installation/).

## Install packages
Install packages with pip and requirements.txt

```
$ pip install -r requirements.txt
```

# Files
## application.py
It contains code for routing.

## helpters.py
It contains code for implement the application such as calling API.

## templates
The folder contains html files for the web page.

## static
The folder has style.css file and images folder which contains image data.

## constants.py
You need to create this file on your local. Put your Open Weather API key on the file like this.
```
OpenWeather_API = 'ABC123ABC123'
```

# Development

## Running the application
To run the application, you can start Flask server by running the following command.

```
FLASK_APP=application.py flask run
```

Then you should see a message

```
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

Go to http://127.0.0.1:5000/ and check the home page.

First, you will be redirected to the login page.
If you don't have an account, go to the registration page (click on `Registration` on header or go to http://127.0.0.1:5000/registration)  and register an account.

When you register for an account, your default location information is set to New York, US. Go to the Setting page (click on robot icon on header or go to http://127.0.0.1:5000/setting) and change it to the correct information.

## Setting data
`country`

Your country to get weather forecast. 
This application supports United States and Canada only.

`zipcode`

Your zip code to get weather forecast.

`Time to leave home`

This is the time for your child to leave home and used as an starting time of the forecast of the day. Enter a number between 0-23.

`Time to return home`

This is the time for your child to return home and used as an ending time of the forecast of the day. Enter a number between 0-23.


## Updating to Next Day's Data
In this application, if you access the page before `Time to return home`, the data for that day will be displayed. After the `Time to return home` time. The date of data is shown on the top of the page, just below the header.

## Data from APIs

### Forecast Data
The application calls the future weather forecast data when you visit the page before `Time to return home`. One Call API (https://openweathermap.org/api/geocoding-api) from OpenWeather.

### History Data
The application calls both the future weather forecast data and the historical weather data when you visit the page between `Time to leave home` and `Time to return home`. One Call API from OpenWeather.

### Geocoding
The application geocodes from country name and zip code to latitude and longitude when it calls the weather forecast and history data. Geocoding API (https://openweathermap.org/api/geocoding-api) from OpenWeather.

## Databased
Your data is stored in two databases `users` and `user_locations`.

### users
- id(integer): primary key
- username(text): unique, not null
- hash(text): hashed password, not null

### user_locations
- id(integer): primary key
- country(text): `United States` or `Canada`, not null
- zipcode(text): not null
- from_hour(integer): not null
- to_hour(integer): not null
- user_id(integer): REFERENCES users.id, not null

# Future Plan

## Improve site display speed
Make the following changes to improve the display speed of the site. When the application calls the API, the data is saved in the database and reused for the same day and the same location.

## Expand supporting country
For other countries, we will expand the supported area by confirming that the geocoding API works correctly.