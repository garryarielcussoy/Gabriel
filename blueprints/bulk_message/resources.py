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
    
    '''
    The following method is used to sending whatsapp message using csv / xls file.

    :param object self: A must present keyword argument
    :return: Status OK
    '''
    def post(self):
        # Take some inputs
        parser = reqparse.RequestParser()
        parser.add_argument('type', location = 'json', required = True)
        parser.add_argument('csv_file', location = 'json', required = True, type = list)
        parser.add_argument('media_url', location = 'json', required = False)
        parser.add_argument('caption', location = 'json', required = False)
        args = parser.parse_args()

        # ----- Check the required arguments -----
        # For all cases
        if (
            args['type'] == '' or args['type'] is None
            or args['csv_file'] == []
        ):
            return {'message': 'Tipe pesan harus diisi dan file csv / xls tidak boleh kosong'}, 400

        # For file or image type cases
        if args['type'] == 'image' or args['type'] == 'file':
            if args['media_url'] == '' or args['media_url'] is None:
                return {'message': 'Tidak ada file ataupun gambar yang diunggah'}, 400
        
        # Looping through each record on csv_file to send the message
        for record in args['csv_file']:
            # Preparing some requirements needed to send the message
            url = 'https://messages-sandbox.nexmo.com/v0.1/messages'
            sender = "14157386170"
            receiver = record['to_number']
            text_message = record['text_message']
            auth = ('8fe08f4c', 'Mz1oxyxiDZoicksE')
            header = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            '''
            For text message type case
            '''
            if args['type'] == 'text':
                # Compose the message
                data = {
                    'from': {'type': 'whatsapp', 'number': sender},
                    'to': {'type': 'whatsapp', 'number': receiver},
                    'message': {
                        'content': {
                            'type': 'text',
                            'text': text_message
                        }
                    }
                }

                # Turn json dictionary into json string
                data = json.dumps(data)

                # Send the message
                response = requests.post(url, data = data, headers = header, auth = auth)
        
            '''
            For image message type case
            '''
            if args['type'] == 'image':
                # Compose the message
                data = {
                    'from': {'type': 'whatsapp', 'number': sender},
                    'to': {'type': 'whatsapp', 'number': receiver},
                    'message': {
                        'content': {
                            'type': 'image',
                            'image': {
                                'url': args['media_url'],
                                'caption': args['caption']
                            }
                        }
                    }
                }

                # Turn json dictionary into json string
                data = json.dumps(data)

                # Send the message
                response = requests.post(url, data = data, headers = header, auth = auth)

        # Return a message
        return {'message': 'Semua pesan sedang dikirim'}, 200
    
# Endpoint in problem-collection route
api.add_resource(BulkMessage, '')