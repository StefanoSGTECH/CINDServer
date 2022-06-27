from numpy import DataSource
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import csv
import pandas as pd
import os
from flask_jwt_extended import get_jwt_identity, jwt_required
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

data = Blueprint("datas", __name__, url_prefix="/api/v1/datas")

@data.post('/add')
@jwt_required()
@cross_origin()
def post_datas():
    current_user = get_jwt_identity()
    email = request.get_json().get('email', '')
    firstName = request.get_json().get('firstName', '')
    lastName = request.get_json().get('lastName', '')
       
    cursor.execute(f"INSERT INTO datas (email, firstname, lastname, creation, update) VALUES ('{email}', '{firstName}', '{lastName}', CURRENT_DATE, CURRENT_DATE);")
    connection.commit()

    return jsonify({
        'message': "data add",
        'data': {
            'firstName': firstName,
            'lastName': lastName,
            "email": email
        }
    }), HTTP_201_CREATED


@data.post('/addfiledata')
@jwt_required()
@cross_origin()
def post_datasfile():
    current_user = get_jwt_identity()
    filesd = request.files['file']

    dataresp = []
    filesd.save(secure_filename(filesd.filename))
    f = open(filesd.filename, 'rb')
    with open(filesd.filename, 'r') as f:
        reader = pd.read_csv(f, sep=',', header=None)
        for row in reader.values:
            data = str(row[0]).replace(";", ",").split(',')
            cursor.execute(f"INSERT INTO datas (email, firstname, lastname, creation, update) VALUES ('{data[0]}', '{data[1]}', '{data[2]}', CURRENT_DATE, CURRENT_DATE);")
            connection.commit()  
            dataresp.append({
                'firstName': data[0],
                'lastName': data[1],
                "email":data[2]
            })     
    os.remove(filesd.filename)
    
    return jsonify({
        'message': "data add",
        'data': dataresp
    }), HTTP_201_CREATED

@data.get("/all")
@jwt_required()
@cross_origin()
def get_datasall():
    #current_user = get_jwt_identity()

    cursor.execute("SELECT * FROM datas;")
    datas = cursor.fetchall()

    if not datas:
        return jsonify({'message': 'datas not found'}), HTTP_404_NOT_FOUND

    dataresp = []

    for data in datas:
        dataresp.append({
            'id': data[0],
            'email': data[1],
            'firstName': data[2],
            'lastName': data[3],
            'creation': data[4],
            'update': data[5],
        })

    return jsonify({
        'data': dataresp
    }), HTTP_200_OK

@data.get("/<int:id>")
@jwt_required()
@cross_origin()
def get_data(id):
    #current_user = get_jwt_identity()

    cursor.execute("SELECT * FROM datas WHERE id='"+str(id)+"';")
    datas = cursor.fetchall()

    if not datas:
        return jsonify({'message': 'datas not found'}), HTTP_404_NOT_FOUND

    dataresp = []

    for data in datas:
        dataresp.append({
            'id': data[0],
            'email': data[1],
            'firstName': data[2],
            'lastName': data[3],
            'creation': data[4],
            'update': data[5],
        })

    return jsonify(dataresp[0]), HTTP_200_OK


@data.delete("/<int:id>")
@jwt_required()
@cross_origin()
def delete_bookmark(id):
    #current_user = get_jwt_identity()

    cursor.execute(f"DELETE FROM datas WHERE id='{id}';")
    connection.commit()

    #if not bookmark:
    #    return jsonify({'message': 'datas not found'}), HTTP_404_NOT_FOUND

    return jsonify({}), HTTP_204_NO_CONTENT

@data.put('/<int:id>')
@data.patch('/<int:id>')
@jwt_required()
@cross_origin()
def editdatas(id):
    urrent_user = get_jwt_identity()
    email = request.get_json().get('email', '')
    firstName = request.get_json().get('firstName', '')
    lastName = request.get_json().get('lastName', '')
       
    cursor.execute(f"UPDATE datas SET email='{email}', firstname='{firstName}', lastname='{lastName}' WHERE id='{id}';")
    connection.commit()

    return jsonify({
        'message': "data edit",
        'data': {
            'firstName': firstName,
            'lastName': lastName,
            "email": email
        }
    }), HTTP_201_CREATED