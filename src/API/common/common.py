from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.API.database import Bookmark, db
from flasgger import swag_from
from flask_cors import CORS, cross_origin

common = Blueprint("commons", __name__, url_prefix="/api/v1/common")


@common.get("/navigation")
@jwt_required()
@cross_origin()
def get_common_navigation():
    #Implement state user
    #current_user = get_jwt_identity()

    navvalue = [
        {
            'id'   : 'dashboard',
            'title': 'Home',
            'type' : 'basic',
            'icon' : 'heroicons_outline:home',
            'link' : '/dashboard'
        },
        {
            'id'   : 'insert',
            'title': 'Inserimento',
            'type' : 'basic',
            'icon' : 'heroicons_outline:plus',
            'link' : '/insert'
        },
        {
            'id'   : 'report',
            'title': 'Report',
            'type' : 'basic',
            'icon' : 'heroicons_outline:chart-pie',
            'link' : '/report'
        }
    ]

    return jsonify({
        'compact': navvalue,
        'default': navvalue,
        'futuristic': navvalue,
        'horizontal': navvalue
    }), HTTP_200_OK


