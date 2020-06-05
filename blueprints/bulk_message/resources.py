# Import from standard libraries
import json
import math
import requests
from datetime import datetime, timedelta, date

# Import from related third party
from blueprints import db, app, admin_required
from flask import Blueprint
from flask_restful import Api, reqparse, Resource, marshal, inputs
from flask_jwt_extended import jwt_required, get_jwt_claims
from sqlalchemy import desc
from celery import Celery

# Import models
from blueprints.user.model import User
from blueprints.message.model import Message
from blueprints.product.model import Product

# Import tasks
from .tasks import bulk_message_text, bulk_message_image, bulk_message_file

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
    
    '''
    The following method is used to sending whatsapp message using csv / xls file.

    :param object self: A must present keyword argument
    :return: Status OK
    '''
    @jwt_required
    def post(self):
        # Take some inputs and claim
        parser = reqparse.RequestParser()
        parser.add_argument('csv_file', location = 'json', required = True, type = list)
        args = parser.parse_args()
        claim = get_jwt_claims()

        # Check the required argument
        if args['csv_file'] == '' or args['csv_file'] == [] or args['csv_file'] is None:
            return {'message': 'Tidak ada file CSV / XLS yang diunggah'}, 400
        
        # Looping through each record on csv_file to send the message
        for record in args['csv_file']:
            # Get user ID
            username = claim['username']
            user = User.query.filter_by(username = username).first()
            user_id = user.id

            # Get related product
            product = Product.query.filter_by(user_id = user_id).filter_by(name = record['product_name']).first()
            if product is None:
                continue

            # Preparing some requirements needed to send the message
            product_id = product.id
            to_number = record['to_number']

            '''
            For text message type case
            '''
            if record['type'] == 'text':
                # Call related task and process it on background
                text_message = record['text_message']
                bulk_message_text.s(product_id, to_number, text_message, 'general', record['receiver'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")).apply_async()
        
            '''
            For image message type case
            '''
            if record['type'] == 'image':
                # Call related task and process it on background
                bulk_message_image.s(product_id, to_number, record['media_url'], record['caption'], record['receiver'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")).apply_async()
            
            '''
            For file message type case
            '''
            if record['type'] == 'file':
                # Call related task and process it on background
                bulk_message_file.s(product_id, to_number, record['media_url'], record['caption'], record['receiver'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")).apply_async()

        # Return a message
        return {'message': 'Sedang mengirim pesan'}, 200
    
# Endpoint in /bulk_message route
api.add_resource(BulkMessage, '')