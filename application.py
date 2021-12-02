import os
import requests
import json
import sqlite3
import pycountry

from sqlite3 import Error
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect,session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import get_output, select_clothes, add_items, database_setup, create_connection, call_geocoding_api, parse_geocode, is_valid_int, display_time

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, uid):
        self.id = uid

@login_manager.user_loader
def load_user(uid):
    return User(uid)

weatherdict = {
    200:'bolt',
    201:'bolt',
    202:'bolt',
    210:'bolt',
    211:'bolt',
    212:'bolt',
    221:'bolt',
    230:'bolt',
    231:'bolt',
    232:'bolt',
    300:'cloud-rain',
    301:'cloud-rain',
    302:'cloud-rain',
    310:'cloud-rain',
    311:'cloud-rain',
    312:'cloud-rain',
    313:'cloud-rain',
    314:'cloud-rain',
    321:'cloud-rain',
    500:'cloud-showers-heavy',
    501:'cloud-showers-heavy',
    502:'cloud-showers-heavy',
    503:'cloud-showers-heavy',
    504:'cloud-showers-heavy',
    511:'cloud-showers-heavy',
    520:'cloud-showers-heavy',
    521:'cloud-showers-heavy',
    522:'cloud-showers-heavy',
    531:'cloud-showers-heavy',
    600:'snowflake',
    601:'snowflake',
    602:'snowflake',
    611:'snowflake',
    612:'snowflake',
    613:'snowflake',
    615:'snowflake',
    616:'cloud-rain',
    620:'snowflake',
    621:'snowflake',
    622:'snowflake',
    701:'cloud-rain',
    711:'smog',
    721:'smog',
    731:'smog',
    741:'smog',
    751:'smog',
    761:'smog',
    762:'meteor',
    771:'cloud-showers-heavy',
    781:'wind',
    800:'sun',
    801:'sun',
    802:'cloud-sun',
    803:'cloud-sun',
    804:'cloud',
}



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            errorMsg = "must provide username"
            return render_template("login.html", errorMsg = errorMsg)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            errorMsg = "must provide password"

       # create a database connection
        conn = create_connection(r"/Users/shizuka/CS50/project/sqlite/simpleweather.db")
        db = conn.cursor()

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = (?)", [username]).fetchall()
        conn.close()

        stored_hash = rows[0][2]

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(stored_hash, password):
            errorMsg = "invalid username and/or password"
            return render_template("login.html", errorMsg = errorMsg)

        # Let user log in
        user = User(rows[0][0])
        login_user(user)
        
        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    errorMsg = None

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        if not username:
            errorMsg = "must provide username"
            return render_template("register.html", errorMsg = errorMsg)

        # Ensure password was submitted
        password = request.form.get("password")
        if not password:
            errorMsg = "must provide password"
            return render_template("register.html", errorMsg = errorMsg)

        # Ensure confirmation was submitted
        confirmation = request.form.get("confirmation")
        if not confirmation:
            errorMsg = "must provide confirmation"
            return render_template("register.html", errorMsg = errorMsg)

        elif not password == confirmation:
            errorMsg = "must match the passwords"
            return render_template("register.html", errorMsg = errorMsg)

        # Create a database connection
        conn = create_connection(r"/Users/shizuka/CS50/project/sqlite/simpleweather.db")
        db = conn.cursor()

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall()

        # Ensure username is not exists
        if len(rows) != 0:
            errorMsg = "existing username"
            return render_template("register.html", errorMsg = errorMsg)

        hashedpw = generate_password_hash(password)

        # Insert new user into users table
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashedpw))
        user = db.execute("SELECT id FROM users WHERE username = ?", [username]).fetchall()
        db.execute("INSERT INTO user_locations (from_hour, to_hour, country, zipcode, user_id) VALUES (?, ?, ?, ?, ?)", (8, 18, 'United States', '10011', user[0][0]))
        conn.commit()
        conn.close()

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", errorMsg = errorMsg)


@app.route("/")
@login_required
def index():
    # Get current user
    user_id = current_user.id

    # Get current datetime
    dt_utc = datetime.now(timezone.utc)
    current_hour_utc = int(dt_utc.strftime('%H'))

    #Get time lag from UTC
    dt_current = datetime.now()
    time_lag_sec = (dt_current - dt_utc.replace(tzinfo=None)).total_seconds()
    time_lag = round(time_lag_sec / (60 * 60))

    # Create a database connection
    conn = create_connection(r"/Users/shizuka/CS50/project/sqlite/simpleweather.db")
    db = conn.cursor()

    # Call for user's setting
    user_location = db.execute("SELECT * FROM user_locations WHERE user_id = ?", user_id).fetchall()
    conn.close()

    country = user_location[0][1]
    zipcode = user_location[0][2]
    from_hour = user_location[0][3] - time_lag
    to_hour = user_location[0][4] - time_lag

    if current_hour_utc <= to_hour:
        month = dt_utc.strftime('%B')
        date = dt_utc.strftime('%d')
        weekday = dt_utc.strftime('%A')

    geoResponse = call_geocoding_api(country, zipcode)
    geocode = parse_geocode(geoResponse)
    lat = geocode['lat']
    lon = geocode['lon']

    output = get_output(country, zipcode, from_hour, to_hour, current_hour_utc, lat, lon)

    weather1 = display_time(user_location[0][3])
    weather3 = display_time(user_location[0][4])
    weather2 = display_time(int((user_location[0][3] + user_location[0][4]) / 2))
    hours = user_location[0][4] - user_location[0][3]
     
    weathers = []
    featured_weather = []
    feels_likes = []
    for i in range(len(output)):
        feels_likes.append(output[i]["feels_like"])
        weatherunicode = weatherdict[output[i]["weather"]]
        weathers.append(weatherunicode)
        if i in (0, int(hours/2), hours):
            featured_weather.append(weatherunicode)

    clothes = select_clothes(feels_likes)
    clothes = add_items(clothes, weathers)
   
    return render_template("index.html", clothes = clothes, clothes_num = len(clothes), weather = featured_weather, month = month, date = date, weekday = weekday, weather1 = weather1, weather2 = weather2, weather3 = weather3)
    

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    # Get current user
    user_id = current_user.id

    # create a database connection
    conn = create_connection(r"/Users/shizuka/CS50/project/sqlite/simpleweather.db")
    db = conn.cursor()

    # Call for user's setting
    user_location = db.execute("SELECT * FROM user_locations WHERE user_id = ?", user_id).fetchall()

    country = user_location[0][1]
    zipcode = user_location[0][2]
    from_hour = user_location[0][3]
    to_hour = user_location[0][4]
    
    # print(country)

    if request.method =="POST":
        
        from_hour = request.form.get("from_hour")
        # Ensure from_hour is provided
        if not from_hour:
            return render_template("settings.html", from_hour = None, to_hour = to_hour, country = country, zipcode = zipcode, errorMsg = "Please input from hour")

        # Ensure from_hour is integer 0 to 23
        if is_valid_int(from_hour) == False:
            return render_template("settings.html", from_hour = None, to_hour = to_hour, country = country, zipcode = zipcode, errorMsg = "Please input integer (0 to 23) as from hour")

        # if request.form.get("from_hour"):
        to_hour = request.form.get("to_hour")
        if not to_hour:
            return render_template("settings.html", from_hour = from_hour, to_hour = None, country = country, zipcode = zipcode, errorMsg = "Please input to hour")

        # Ensure to_hour is integer 0 to 23
        if is_valid_int(to_hour) == False:
            return render_template("settings.html", from_hour = from_hour, to_hour = None, country = country, zipcode = zipcode, errorMsg = "Please input integer (0 to 23) as to hour")

        # if request.form.get("country"):
        country = request.form.get("country")
        if not country:
            return render_template("settings.html", from_hour = from_hour, to_hour = to_hour, country = None, zipcode = zipcode, errorMsg = "Please input to country")        

        # if request.form.get("zipcode"):
        zipcode = request.form.get("zipCode")
        if not zipcode:
            return render_template("settings.html", from_hour = from_hour, to_hour = to_hour, country = country, zipcode = None, errorMsg = "Please input zip code")

        #Update the latest chsh after the transaction
        db.execute("UPDATE user_locations SET from_hour = ?, to_hour = ?, country = ?, zipcode = ? WHERE user_id = ?", (from_hour, to_hour, country, zipcode, user_id))
        conn.commit()
        conn.close()
        
        return redirect("/")

    else:
         # Get current user
        user_id = current_user.id

        # Create a database connection
        conn = create_connection(r"/Users/shizuka/CS50/project/sqlite/simpleweather.db")
        db = conn.cursor()

        # Call for user's setting
        user_location = db.execute("SELECT * FROM user_locations WHERE user_id = ?", user_id).fetchall()
        conn.close()

        country = user_location[0][1]
        zipcode = user_location[0][2]
        from_hour = user_location[0][3]
        to_hour = user_location[0][4]

        return render_template("settings.html", from_hour = from_hour, to_hour = to_hour, country = country, zipcode = zipcode)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():

    if request.method =="POST":
        print("Tyring to log put")
        logout_user()
        return redirect("/")

    else:
        return render_template("logout.html")


@app.route("/attribution")
def attribution():
    return render_template("attribution.html")
