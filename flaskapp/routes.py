import json


from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from flaskapp.forms import LoginForm, RegistrationForm, AdminRegistrationForm
from flaskapp import db, bcrypt

from flask_login import login_user, current_user, logout_user, login_required

from flaskapp.models import User, Post, Role, Test


posts = [
    {
        'author': 'abc',
        'title': 'Blog Post 1',
        'content': 'Blog Post',
        'date_posted': 'April 20, 3045'
    }, {
        'author': 'sdf',
        'title': 'kalu Post 1',
        'content': 'kalu Post',
        'date_posted': 'April 21, 2018'
    }
]

routes = Blueprint('routes', __name__)

@routes.route("/")
@routes.route("/home")
def home():
    return render_template('home.html', posts=posts)


@routes.route("/about")
def about():
    return render_template('about.html', title='About')


@routes.route("/register", methods=['GET', 'POST'])
def register_form():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    password=bcrypt.generate_password_hash(form.password.data))
        user_role = Role.query.filter_by(name="User").first()
        user.role.append(user_role)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data} successfully, YOu can now loggin', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', title='Register', form=form)


@routes.route("/admin-register", methods=['GET', 'POST'])
def register_admin():
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data,
                    password=bcrypt.generate_password_hash(form.password.data))
        user_role = Role.query.filter_by(name="Admin").first()
        user.role.append(user_role)
        db.session.add(user)
        db.session.add(user_role)
        db.session.commit()
        flash(f'Account created for {form.username.data} successfully, YOu can now loggin', 'success')
        return redirect(url_for('routes.login'))
    return render_template('admin-register.html', title='Admin-Register', form=form)


# @app.route("/login", methods=['GET', 'POST'])
# def login_form():
#     if current_user.is_authenticated:
#         return redirect(url_for('home'))
#     form = LoginForm()
#     if form.validate_on_submit:
#         user = User.query.filter_by(email=form.email.data).first()
#         if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
#             login_user(user, remember=form.remember.data)
#             next_page = request.args.get('next')
#             if next_page:
#                 return redirect(url_for(next_page))
#             return redirect(url_for('home'))
#             flash(f'Logged in as {user.username}', 'success')
#         else:
#             flash("Login Unsuccessful. Please enter your email and password", 'danger')
#     return render_template('login.html', title='Login', form=form)

@routes.route("/logout")
def logout_function():
    logout_user()
    return redirect(url_for('routes.home'))


@routes.route("/account")
@login_required
def account_user():
    return render_template('account.html', title='Account')


@routes.route("/test", methods=['GET', 'POST'])
def test_page():
    data = request.get_json()
    print(data)
    print(data.get('name'))
    print(data.get('surname'))
    return 'done'


@routes.route("/user", methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    # Check if user exists
    if user:
        return jsonify({'message': 'User found', 'name': user.name})
    else:
        return jsonify({'message': 'User not found'}), 404


@routes.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    print('Received data:', username, password)

    user = User.query.filter_by(email=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        # print(json.dumps(user.toDict()))
        user = dict(roles=list(user.getUserRole()), email=user.email, username=user.username)
        return jsonify({"user":user, 'access_token': access_token})
    else:
        return jsonify({'message': 'Login Failed'}), 401
    
@routes.route('resturants', methods=["POST", "GET"])
def resturants():
    data = request.get_json()
    
