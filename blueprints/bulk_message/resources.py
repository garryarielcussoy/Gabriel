# Import from standard libraries
import json
import math
from datetime import datetime, timedelta, date

# Import from related third party
from blueprints import db, app, admin_required
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from flask_jwt_extended import jwt_required, get_jwt_claims
from sqlalchemy import desc

# Import models
from blueprints.user.model import User
from blueprints.message.model import Message

# Creating blueprint
bp_bulk_message = Blueprint('bulk_message', __name__)
api = Api(bp_bulk_message)

'''
The following class is designed for bulk messaging.
'''
class BulkMessage(Resource):
    '''
    The following method is designed to prevent CORS.

    :param object self: A must present keyword argument
    :return: Status OK
    '''
    def options(self):
        return {'status': 'ok'}, 200
    
# Endpoint in problem-collection route
api.add_resource(BulkMessage, '')