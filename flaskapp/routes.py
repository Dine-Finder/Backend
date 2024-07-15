import re
import json
import os
from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_cors import cross_origin
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token
from flask_login import login_user, logout_user, current_user
from flaskapp import db, bcrypt
from flaskapp.forms import AdminRegistrationForm
from flaskapp.models import User, Role
from werkzeug.exceptions import HTTPException
import googlemaps
from .restaurants import get_filters
from dotenv import load_dotenv

routes = Blueprint('routes', __name__)

# Custom Error Handlers
@routes.errorhandler(HTTPException)
def handle_http_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    return jsonify(error=str(e), description=e.description), e.code

@routes.errorhandler(404)
def handle_404_error(e):
    return jsonify(error='Not found', description='The resource was not found'), 404

@routes.errorhandler(500)
def handle_500_error(e):
    return jsonify(error='Server error', description='An internal server error occurred'), 500

# Admin Registration
@routes.route("/admin-register", methods=['GET', 'POST'])
def register_admin():
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user_role = Role.query.filter_by(name="Admin").first()
        user.role.append(user_role)
        db.session.add(user)
        db.session.commit()
        flash('Account created for {} successfully, You can now login'.format(form.username.data), 'success')
        return redirect(url_for('routes.login'))
    return render_template('admin-register.html', title='Admin-Register', form=form)

def is_valid_email(email):
    """Validate the email format."""
    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.match(email_regex, email, re.IGNORECASE)

def is_strong_password(password):
    """Check if the password is strong."""
    return len(password) >= 8 and re.search(r"[a-zA-Z]", password) and re.search(r"\d", password)

@routes.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(email=data['username']).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({'user': {'username': user.username, 'email': user.email}, 'access_token': access_token})

@routes.route("/api/register", methods=['POST'])
def register_form():
    if current_user.is_authenticated:
        return jsonify({'message': 'Already authenticated'}), 400

    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data or 'username' not in data:
        return jsonify({'message': 'Missing required fields'}), 400

    if not is_valid_email(data['email']):
        return jsonify({'message': 'Invalid email format'}), 422

    if not is_strong_password(data['password']):
        return jsonify({'message': 'Password must be at least 8 characters long and include letters and numbers'}), 422

    user = User.query.filter_by(email=data['email']).first()
    if user:
        return jsonify({'message': 'Email already used'}), 409

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    user_role = Role.query.filter_by(name="User").first()
    new_user.role.append(user_role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registration successful'}), 201


# User Logout
@routes.route("/api/logout")
def logout_function():
    if not current_user.is_authenticated:
        return jsonify({'message': 'No user is currently logged in'}), 403

    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

# Get User Information
@routes.route("/user", methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify({'username': user.username, 'email': user.email})
    return jsonify({'message': 'User not found'}), 404

@routes.route('/api/resturants', methods=["POST", "GET"])
def resturants():
    if request.method == "POST":
        load_dotenv()
        gmaps = googlemaps.Client(key=os.getenv("REACT_APP_GOOGLE_MAPS_API_KEY"))
        data = request.get_json()
        preferences = data.get("input", {})
        neighborhood = preferences["location"]["neighborhood"]
        if neighborhood != "":
            place_name = neighborhood + ", Manhattan, NY"
            geocode_result = gmaps.geocode(place_name)
            if geocode_result:
                # Extract latitude and longitude
                latitude = geocode_result[0]['geometry']['location']['lat']
                longitude = geocode_result[0]['geometry']['location']['lng']
            else:
                return jsonify({"response": "No Restaurants from selected preference"})
        else:
            latitude = preferences["location"]["coordinates"][0]
            longitude = preferences["location"]["coordinates"][1]
            if not latitude or not longitude:
                return jsonify({"response": "No Restaurants from selected preference"})

        radius = preferences["location"]["radius"]
        if not radius:
            radius = 1
        else:
            radius = float(radius)
        day = preferences["dayTime"]["day"]
        time = int(preferences["dayTime"]["time"])
        localBusyness = preferences["localeBusyness"]
        restaurantBusyness = preferences["restaurantBusyness"]

        output = get_filters(float(latitude), float(longitude), radius, day, time, localBusyness, restaurantBusyness)

        if not output.empty:
            result_json = output.to_json(orient="records")
            return jsonify({"response": "Received", "output": json.loads(result_json)})
        else:
            return jsonify({"response": "No Restaurants from selected preference"})

    return jsonify({"message": "GET method not allowed"}), 405