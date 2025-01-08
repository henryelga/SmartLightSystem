import os
from flask import Flask, render_template, jsonify, redirect, url_for, session, flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv
import pymysql

import my_db

load_dotenv()

db = my_db.db

app = Flask(__name__)

# App Configuration
app.secret_key = "topSecret123"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# Checking for default or no password
def check_database_credentials(uri):
    try:
        # Parse URI
        user = uri.split('//')[1].split(':')[0]
        password = uri.split(':')[2].split('@')[0]
        
        # Check for default or empty password
        if not password or password in ["root", "admin", "password", "", ""]:
            print("⚠️ Warning: The database is using a default or no password. Please secure your database!")
        
        connection = pymysql.connect(
            host=uri.split('@')[1].split('/')[0],
            user=user,
            password=password,
        )
        connection.close()
    except Exception as e:
        print("⚠️ Error while checking database credentials:", e)

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:@127.0.0.1/smart_light'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

check_database_credentials(app.config["SQLALCHEMY_DATABASE_URI"])

db.init_app(app)



if os.getenv("OAUTHLIB_INSECURE_TRANSPORT") == "1":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

google_bp = make_google_blueprint(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    redirect_to="google_login",
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
)
app.register_blueprint(google_bp, url_prefix="/login")

@app.route("/")
# Redirect to home if the user is already logged in
def index():
    if "user" in session and session["user"] != "Guest":
        return redirect(url_for("home"))
    else:
        return render_template("index.html")

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("login")) 

    response = google.get("https://www.googleapis.com/oauth2/v1/userinfo")
    if not response.ok:
        print("Error response:", response.text)
        return "Error: Unable to fetch user information from Google."

    user_info = response.json()
    print("User Info:", user_info)

    # Store user info in the session
    session["user"] = user_info.get("name", "Unknown User")
    session["email"] = user_info.get("email", "No email provided")
    session["google_client_id"] = user_info.get("id")

    # Add user to the database or update login status
    my_db.add_user_and_login(
        name=user_info.get("name", "Unknown User"),
        google_client_id=user_info.get("id"),
        email=user_info.get("email", "No email provided"),
        token=None, 
    )

    return redirect(url_for("home"))


# logout route
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("index"))

@app.route("/not_authorized")
def not_authorized():
    return render_template("not_authorized.html") 


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session or session["user"] == "Guest":
            return redirect(url_for("not_authorized"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/home")
@login_required
def home():
    user = session.get("user", "Guest")
    email = session.get("email", "No email provided")

    return render_template(
        "home.html",
        user=user,
        email=email,
    )

if __name__ == "__main__":
    app.run(debug=True)
