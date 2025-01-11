import os
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv
import pymysql

import my_db, pb

load_dotenv()

db = my_db.db

app = Flask(__name__)

# app Configuration
app.secret_key = "sec-c-YTYyZmQ3YTItYzc1ZS00NjMwLTlkNGQtOTFmODM1ZTYyNzBk"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# checking for default or no password
def check_database_credentials(uri):
    try:
        # parse URI
        user = uri.split('//')[1].split(':')[0]
        password = uri.split(':')[2].split('@')[0]
        
        # check for default or empty password
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

GOOGLE_CLIENT_ID = "369450398481-b8c4p4lv4h5v823tt0aq6i9m7fd2999q.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"

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
# redirect to home if the user is already logged in
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

    # store user info in the session
    session["user"] = user_info.get("name", "Unknown User")
    session["email"] = user_info.get("email", "No email provided")
    session["google_client_id"] = user_info.get("id")

    # add user to the database or update login status
    my_db.add_user_and_login(
        name=user_info.get("name", "Unknown User"),
        google_client_id=user_info.get("id"),
        email=user_info.get("email", "No email provided"),
        token=None, 
    )
    
    token = pb.generate_token(user_info.get("id"))

    if token:
        my_db.update_user_token(user_info.get("id"), token)
        session["token"] = token 

    return redirect(url_for("home"))


# logout route
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("index"))

# not_authorized route
@app.route("/not_authorized")
def not_authorized():
    return render_template("not_authorized.html") 

# login required
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
    google_client_id = session.get("google_client_id", "No client_id provided")
    
    token = None
    
    user_record = my_db.get_user_row_if_exists(google_client_id)
    if user_record:
        token = user_record.token

    return render_template(
        "home.html",
        user=user,
        email=email,
        google_client_id=google_client_id,
        token=token,
    )
    
last_motion_detected = False 
last_beam_status = "Not Broken"
last_light_status = "Off"

@app.route('/add_event', methods=['POST'])
def add_event():
    global last_motion_detected, last_beam_status, last_light_status 

    # get data from the request
    data = request.get_json()

    # update motion_detected, keeping track of the last known value
    motion_detected = data.get('motion_detected')
    if motion_detected is not None:
        last_motion_detected = motion_detected 
    else:
        motion_detected = last_motion_detected  

    beam_status = data.get('beam_status')
    if beam_status is not None:
        last_beam_status = beam_status  
    else:
        beam_status = last_beam_status 

    light_status = data.get('light_status')
    if light_status is not None:
        last_light_status = light_status
    else:
        light_status = last_light_status  

    manual_control = data.get('manual_control') or False 

    my_db.add_event(motion_detected, beam_status, light_status, manual_control)

    return jsonify({"message": "Event processed successfully"}), 201

@app.route("/dashboard")
@login_required
def dashboard():
    # retrieve all events from the database
    events = my_db.get_all_events()
    user = session.get("user", "Guest")

    return render_template("dashboard.html", events=events, user=user)    

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/refresh_user_token", methods=["POST"])
def refresh_user_token():
    try:
        user_uuid = session.get("google_client_id")
        if not user_uuid:
            return jsonify({"error": "User not logged in"}), 401

        new_token = pb.refresh_token(user_uuid, ttl=5)

        if not new_token:
            return jsonify({"error": "Failed to refresh token"}), 500

        my_db.update_user_token(user_uuid, new_token)

        session["token"] = new_token

        return jsonify({"success": True, "token": new_token}), 200
    except Exception as e:
        print(f"Error in refresh_token_endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
