from datetime import timedelta
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, set_access_cookies, set_refresh_cookies
import validators
from flask import Blueprint, request, jsonify, make_response
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from werkzeug.security import check_password_hash, generate_password_hash
from src.database import User, db

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.get('/')
def get_all():
    return []

@auth.post('/register')
def register_user():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if len(password) < 6:
        return jsonify({'error': 'password is too short'}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': 'username is too short'}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or ' ' in username:
        return jsonify({'error': 'username should be alphanumeric, and no spaces'}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': 'email is not valid'}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'email is taken'}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'error': 'username is taken'}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)

    user = User(username=username, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'user created',
        'user': {
            'username': username,
            'email': email
        }
    }), HTTP_201_CREATED
@auth.post('/login')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)
        if is_pass_correct:
            refresh_expiration = timedelta(days=30)
            refresh = create_refresh_token(identity=user.id, expires_delta=refresh_expiration)
            access_expiration = timedelta(hours=1)  # Adjust as per your requirements
            access = create_access_token(identity=user.id, expires_delta=access_expiration)

            # Set cookies in the response
            response = make_response(
                jsonify({
                    'user': {
                        'refresh': refresh,
                        'access': access,
                        'username': user.username,
                        'email': user.email
                    }
                }), HTTP_200_OK
            )
            set_access_cookies(response, access)
            set_refresh_cookies(response, refresh)
            return response
        return jsonify({'error': 'wrong credentials'}), HTTP_401_UNAUTHORIZED
    else: 
        return 'failed'

@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
 
    return jsonify({
        'username': user.username,
        'email': user.email
    }), HTTP_200_OK

@auth.post('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity() 
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), HTTP_200_OK



