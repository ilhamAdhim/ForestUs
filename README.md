This is a web application project that helps people to donate and see 
latest posts that concerns more to environmental stuffs

static/ : is used to store bootstrap and images
templates/ : to store HTML codes with Jinja template to enable us presenting the data based on server's response
app.py : set endpoints , login with google , handling posts and user , donations ,etc
db.py : Configure the database for user
posts.py : Posts information served as directory in Python. Not a good approach but it works
requirements.txt : From the list, you only need to install pymysql and flask. Install it by using pip package manager for Python
schema.sql : simple one table database, used to store user's information
user.py : Connects python with the sqlite database. Insert new record in the database if new user has registered, and acquire the logged-in user's information as a session.

