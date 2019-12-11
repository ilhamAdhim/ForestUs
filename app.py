# Python standard libraries
import json
import os
import sqlite3
import random,math
from posts import *
from datetime import datetime
from userContribution import * 

# client id : 730511995699-p169sp9bm67106l525tq9us7e0vj0t56.apps.googleusercontent.com
# client secret : HRAlXTZ2muE4wglXRTkQ-4om

# Third-party libraries
from flask import Flask, redirect, request, url_for, render_template
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from db import init_db_command
from user import User





# Recommended Configuration
# GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
# GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)

# Naive config
GOOGLE_CLIENT_ID = "730511995699-p169sp9bm67106l525tq9us7e0vj0t56.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "HRAlXTZ2muE4wglXRTkQ-4om"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


# Flask app setup
app = Flask(__name__)
# os.environ.get("SECRET_KEY") or
app.secret_key = os.urandom(24)

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Index endpoint
@app.route("/")
@app.route("/login")
def index():
    if current_user.is_authenticated:
        highlight_news = news[:3]
        highlight_donation = donation[:3]
        # return (
        #     "<p>Hello, {}! You're logged in! Email: {}</p>"
        #     "<div><p>Google Profile Picture:</p>"
        #     '<img src="{}" alt="Google profile pic"></img></div>'
        #     '<a class="button" href="/logout">Logout</a>'.format(
        #         current_user.name, current_user.email, current_user.profile_pic
        #     )
        # )
        return render_template('home.html'
        , current_user=current_user
        , login=True if current_user.is_authenticated else False
        , title="Home"
        , news_list =highlight_news
        , donation_list = highlight_donation)

    else:
        # return '<a class="button" href="/login">Google Login</a>'
        return render_template('login.html')

# Skip sign up / login
@app.route("/Home")
def skip():
    highlight_news = news[:3]
    highlight_donation = donation[:3]
    return render_template('home.html',
     login=False,
     title="Home",
     news_list = highlight_news,
     donation_list = highlight_donation)

# Login Endpoint
@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
# The user authenticated with Google, authorized your
# app, and now you've verified their email through Google!
    age = random.randrange(18, 30)
    nations = ('India', 'Guinea', 'Malaysia', 'Indonesia', 'Japan', 'Korea')
    nationality = random.choice(nations)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["name"]

        print(userinfo_response.json())
    else:
        return "User email not available or not verified by Google.", 400

        # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture, age=age, nationality=nationality
    )

    # Doesn't exist? Add it to the database.

    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email,
                    picture, age, nationality)
    # Begin user session by logging the user in
    login_user(user)

    # Send user back to home page
    return redirect(url_for("index"))


# Logout endpoint
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/myProfile")
def myProfile():
    print(current_user.email)
    if current_user.email == "ilhamm179@gmail.com":
        print(current_user.email)

        user_contributing = donation[:3]
        user_contributed = donation[3:5]
    # elif current_user.email is "ilhamavab3l@gmail.com":
    #     user_contributing = donation[:2]
    #     user_contributed = donation[2:4]
    else:
        user_contributing = None
        user_contributed = None
    return render_template('profile.html',
    user=current_user,
    title="Profile",
    login=True if current_user.is_authenticated else False,
    contributing_list = user_contributing,
    contributed_list = user_contributed,
    anyContributed = True if user_contributed != None else False,
    anyContributing=True if user_contributing != None else False )


@app.route("/<int:p_id>/<string:isDonation>/<string:isDonated>/<new_petition>",methods=['GET','POST'])
def each_post(p_id, isDonation,isDonated , new_petition):
    return render_template('each_post.html',
    isDonation=True if isDonation== "True" else False,
    isDonated=True if isDonated== "True" else False,
    login=True if current_user.is_authenticated else False,
    post=donation[p_id] if isDonation == "True" else news[p_id],
    new_petition = new_petition if new_petition != "none" else "none",
    m= math,
    title= 'Post')
    

@app.route("/response_petition/post=<int:p_id>", methods=['GET','POST'])
def response_petition(p_id):
    # if 'isAnonymous' in request.form.getlist('isAnonymous')  :
    #     new_name = "Anonymous"
    # else:
    #     new_name = request.form['fname']
    # user_list = list(map(lambda x: x['user_signed'], donation))
    # name = list(map(lambda x: x['name'], user_list[p_id]))
    # time = list(map(lambda x: x['time_signed'], user_list[p_id]))
    # name.append(new_name)
    # time.append(random.randrange(4,20))
    # new_petition = {
    #     'name' : new_name,
    #     'time_signed' : random.randrange(4,20)
    # }
    return redirect(url_for('each_post'
    , p_id = p_id
    , isDonation = True
    , isDonated = True
    , new_petition = True))

@app.route("/receipt" , methods=['GET', 'POST'])
def donation_receipt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    if request.method == "POST":
        data = request.form.to_dict()
        total_price = int(request.form['frequent']) * int(request.form['price'])
        # ... do something with data ... 
    return render_template('receipt.html',
    current_user=current_user,
    title = "Receipt",
    total = total_price,
    time = dt_string,
    login=True if current_user.is_authenticated else False,
    data = data)

@app.route("/Category=<string:category>")
def each_category(category):
    if category == "Donation":
        lists = donation
    else: 
        lists = news
    return render_template('each_category.html' , lists=lists 
    , title="Donation" if category == "Donation" else "News"
    , category=category
    ,login=True if current_user.is_authenticated else False,
    )

if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')

