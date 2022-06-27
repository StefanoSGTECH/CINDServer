from cgitb import text
from turtle import st

from numpy import number
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
import warnings
import requests
import json
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from
from flask_cors import CORS, cross_origin

common = Blueprint("commons", __name__, url_prefix="/api/v1/common")

def getTokenPB():
    url = 'https://login.microsoftonline.com/common/oauth2/token'

    data = """ grant_type=password
                &username=RiccardoZanini@riccardozanini14.onmicrosoft.com
                &password=RicSte2022!
                &client_id=59b925ce-fdb2-4367-8c6f-10f34b9d5f20
                &client_secret=Pe28Q~qboRqJgygb8CrL6t6G3iO6SOC0S8Jtcdkd
                &resource=https://analysis.windows.net/powerbi/api"""

    r = requests.post(url, data=data, verify=False)
    response_text = json.loads(r.text.encode('utf8'))
    return str(response_text["access_token"])

def getPagesInGroup(groupId: str, reportId: str, token: str):
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    url = f'https://api.powerbi.com/v1.0/myorg/groups/{groupId}/reports/{reportId}/pages'
    headers = {'Authorization': 'Bearer '+ token}
    r = requests.get(url, headers=headers, verify=False)
    response_text = json.loads(r.text.encode('utf8'))
    pagesgroup = []
    pages = response_text["value"]
    for page in pages:
        pageName = page['Name']
        name = page['displayName']
        pagesgroup.append({
                            'id '     : 'reportBI.group.page',
                            'title'   : str(name),
                            'type'    : 'basic',
                            'link'    : '/reportPBI/' + str(reportId) + '/' + str(groupId) + '/' + str(pageName) + '/' + str(token)
                        })
    return pagesgroup

def getPages(groupId: str):
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    token = getTokenPB()
    url = f'https://api.powerbi.com/v1.0/myorg/groups/{groupId}/reports'
    headers = {'Authorization': 'Bearer '+ token}
    r = requests.get(url, headers=headers, verify=False)
    response_text = json.loads(r.text.encode('utf8'))
    pagesPBI = []
    pages = response_text["value"]
    for page in pages:
        id = page['id']
        name = page['name']
        pagesPBI.append({
                    'id '     : 'reportBI.group',
                    'title'   : str(name),
                    'type'    : 'collapsable',
                    'icon'    : 'heroicons_outline:chart-pie',
                    'children': getPagesInGroup(groupId, id, token)
                })

    repsponsejs = {
            'id '     : 'reportBI',
            'title'   : 'Report BI',
            'subtitle': '',
            'type'    : 'group',
            'icon'    : 'heroicons_outline:chart-pie',
            'children': pagesPBI
        }
    return [repsponsejs]

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

    navvalue += getPages('2dad51f0-ab08-48c7-8db2-9c8aca3a120e')

    return jsonify({
        'compact': navvalue,
        'default': navvalue,
        'futuristic': navvalue,
        'horizontal': navvalue
    }), HTTP_200_OK


