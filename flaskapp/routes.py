import re
import json
import os
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, url_for, current_app, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_login import current_user, logout_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.exceptions import HTTPException

from flaskapp import db, bcrypt
from flaskapp.models import User
from flask_mail import Message
import googlemaps
from .restaurants import get_filters
from dotenv import load_dotenv

routes = Blueprint('routes', __name__)
load_dotenv()

@routes.errorhandler(HTTPException)
def handle_http_exception(e):
    return jsonify(error=str(e), description=e.description), e.code

@routes.errorhandler(404)
def handle_404_error(e):
    return jsonify(error='Not found', description='The resource was not found'), 404

@routes.errorhandler(500)
def handle_500_error(e):
    return jsonify(error='Server error', description='An internal server error occurred'), 500

def is_valid_email(email):
    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.match(email_regex, email, re.IGNORECASE)

def is_strong_password(password):
    return len(password) >= 8 and re.search(r"[a-zA-Z]", password) and re.search(r"\d", password)

def send_verification_email(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt=current_app.config['SECURITY_PASSWORD_SALT'])
    verify_url = url_for('routes.verify_email', token=token, _external=True)
    msg = Message('Confirm Your Email', sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.body = f'Please click on the link to verify your email address: {verify_url}'
    current_app.extensions['mail'].send(msg)

@routes.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user is None:
            return jsonify({'message': 'Invalid token or user does not exist'}), 404
        if user.is_confirmed:
            return jsonify({'message': 'Account already verified.'}), 409
        user.is_confirmed = True
        user.confirmed_on = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({'message': 'Email verified successfully. You can now log in.'}), 200
    except SignatureExpired:
        user = User.query.filter_by(email=email).first()
        if user and not user.is_confirmed:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'Verification link expired. Registration not completed, please register again.'}), 410
    except BadSignature:
        return jsonify({'message': 'Invalid or expired token'}), 400

@routes.route('/api/signin', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'message': 'Username and password are required'}), 400
    user = User.query.filter_by(email=data['username']).first()
    if not user:
        return jsonify({'message': 'Invalid username or password'}), 401
    if not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401
    if not user.is_confirmed:
        return jsonify({'message': 'Please verify your email before signing in'}), 403
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
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists. Please choose a different username.'}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already used'}), 409
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password, is_confirmed=False)
    db.session.add(new_user)
    db.session.commit()
    send_verification_email(new_user)
    return jsonify({'message': 'Registration successful. Please check your email to confirm your email address.'}), 201

@routes.route("/api/logout")
def logout_function():
    if not current_user.is_authenticated:
        return jsonify({'message': 'No user is currently logged in'}), 403
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@routes.route("/user", methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user:
        return jsonify({'username': user.username, 'email': user.email})
    return jsonify({'message': 'User not found'}), 404

@routes.route('/api/restaurants', methods=["POST", "GET"])
def restaurants():
    if request.method == "POST":
        data = request.get_json()
        preferences = data.get("input", {})
        neighborhood = preferences["location"]["neighborhood"]
        if neighborhood != "":
            place_name = neighborhood + ", Manhattan, NY"
            geocode_result = current_app.extensions['gmaps'].geocode(place_name)
            if geocode_result:
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


@routes.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'message': 'Email is required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'User with this email does not exist'}), 404

    send_password_reset_email(user)
    return jsonify({'message': 'Password reset email sent successfully'}), 200

def send_password_reset_email(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt=current_app.config['SECURITY_PASSWORD_SALT'])
    reset_url = url_for('routes.reset_password', token=token, _external=True)
    msg = Message('Password Reset Request', sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.body = f'Please click on the link to reset your password: {reset_url}'
    current_app.extensions['mail'].send(msg)

@routes.route('/reset_password/<token>', methods=['GET'])
def reset_password(token):
    try:
        return render_template('reset_password.html', token=token)
    except Exception as e:
        return jsonify({'message': 'The reset link is invalid or has expired.'}), 400

@routes.route('/api/confirm_reset_password/<token>', methods=['GET', 'POST'])
def confirm_reset_password(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=3600)
        user = User.query.filter_by(email=email).first()
        if request.method == 'POST':
            data = request.get_json()
            new_password = data.get('password')
            confirm_password = data.get('confirm_password')

            if not new_password or not confirm_password:
                return jsonify({'message': 'Password and confirm password are required'}), 400
            if new_password != confirm_password:
                return jsonify({'message': 'Passwords do not match'}), 400
            if not is_strong_password(new_password):
                return jsonify({'message': 'Password must be at least 8 characters long and include letters and numbers'}), 422
            
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            return jsonify({'message': 'Password reset successful. You can now log in.'}), 200

    except Exception as e:
        return jsonify({'message': 'The reset link is invalid or has expired.'}), 400