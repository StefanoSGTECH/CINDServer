from os import access

from sqlalchemy import String, null
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask import Blueprint, app, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from flasgger import swag_from
from flask_cors import CORS, cross_origin

import psycopg2
from psycopg2 import Error

# Connect to an existing database
connection = psycopg2.connect(user="postgres",
                                password="sqlpass",
                                host="127.0.0.1",
                                port="5432",
                                database="cind")
# Create a cursor to perform database operations
cursor = connection.cursor()

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post('/register')
@swag_from('../../docs/auth/register.yaml')
@cross_origin()
def register():
    firstname = request.json['firstName']
    lastname = request.json['lastName']
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    cursor.execute("SELECT * FROM users WHERE email='"+str(email)+"';")
    useru = cursor.fetchall()

    if len(password) < 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': "User is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    for user in useru:
        if str(user[3]) == email is not None:
            return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

        if str(user[4]) == username is not None:
            return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT
        
    pwd_hash = generate_password_hash(password)

    cursor.execute(f"INSERT INTO users (firstname, lastname, email, username, password, creation, update) VALUES ('{firstname}', '{lastname}', '{email}', '{username}', '{pwd_hash}', CURRENT_DATE, CURRENT_DATE);")
    connection.commit()

    return jsonify({
        'message': "User created",
        'user': {
            'username': username, "email": email
        }

    }), HTTP_201_CREATED


@auth.post('/login')
@cross_origin()
@swag_from('../../docs/auth/login.yaml')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    cursor.execute("SELECT * FROM users WHERE email='"+str(email)+"';")
    user = cursor.fetchall()[0]

    if user:
        is_pass_correct = check_password_hash(user[5], password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user[0])
            access = create_access_token(identity=user[0])

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user[4],
                    'email': user[3]
                }

            }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@auth.get("/me")
@jwt_required()
@cross_origin()
def me():
    user_id = get_jwt_identity()
    cursor.execute("SELECT * FROM users WHERE id='"+str(user_id)+"';")
    user = cursor.fetchall()[0]

    return jsonify({
        'id': user[0],
        'firstName': user[1],
        'lastName': user[2],
        'email': user[3],
        'username': user[4],
        'avatar': '',
        'status': 'online'    
    }), HTTP_200_OK


@auth.get('/token/refresh')
#@jwt_required(refresh=True)
@jwt_required()
@cross_origin()
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), HTTP_200_OK
