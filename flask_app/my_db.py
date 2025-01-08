from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import and_

db = SQLAlchemy()

# users table
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    google_client_id = db.Column(db.String(255), unique=True)
    token = db.Column(db.String(255))
    login = db.Column(db.Integer)
    read_access = db.Column(db.Integer)     # to change access permissions
    write_access = db.Column(db.Integer)    # to change access permissions
    email = db.Column(db.String(30))

    
    def __init__(self, name, google_client_id, token, login, read_access, write_access, email):
        self.name = name
        self.google_client_id = google_client_id
        self.token = token
        self.login = login
        self.read_access = read_access
        self.write_access = write_access
        self.email = email

def get_user_row_if_exists(google_client_id):
    return User.query.filter_by(google_client_id=google_client_id).first()

def add_user_and_login(name, google_client_id, email, token=None):
    user = get_user_row_if_exists(google_client_id)
    
    if user:
        user.login = 1
        if token:
            user.token = token
        db.session.commit()
    else:
        new_user = User(name, google_client_id, token, 1, 0, 0, email)
        db.session.add(new_user)
        db.session.commit()

def get_user_by_email(email):
    try:
        user = User.query.filter_by(email=email).first()
        
        if user:
            return {"id": user.id, "name": user.name, "email": user.email}
        else:
            return None
    except Exception as e:
        print(f"Error retrieving user by email: {e}")
        return None
    
    
def update_user_token(google_client_id, token):
    user = get_user_row_if_exists(google_client_id)
    if user:
        user.token = token
        db.session.commit()
    else:
        print(f"User with Google Client ID {google_client_id} not found.")

def get_user_token(google_client_id):
    try:
        user = User.query.filter_by(google_client_id=google_client_id).first()
        if user:
            return user.token
        else:
            print(f"User with Google Client ID {google_client_id} not found.")
            return None
    except Exception as e:
        print(f"Error in get_user_token: {e}")
        raise Exception(f"Error fetching user token: {e}")