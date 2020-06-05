# Import from standard libraries
import json
import math
import requests
import random
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
from blueprints.bulk_message.tasks import bulk_message_text

# Creating blueprint
bp_otp = Blueprint('otp', __name__)
api = Api(bp_otp)

'''
The following class is designed to handle OTP process.
'''
class Otp(Resource):
    '''
    The following method is designed to prevent CORS.

    :param object self: A must present keyword argument
    :return: Status OK
    '''
    def options(self):
        return {'status': 'ok'}, 200
    
    '''
    The following method is designed to receive OTP request, generate OTP code, and sent it back to third party and also
    to related end-user.

    :param object self: A must present keyword argument
    :return: to_number: Phone number of end-user who triggered OTP process
    :return: otp_code: The code for verification (a code consists of digits of length six)
    :return: message: Send third party a message which tells that the otp code has been sent to related user
    '''
    @jwt_required
    def post(self):
        # Take some inputs and claims
        parser = reqparse.RequestParser()
        parser.add_argument('to_number', location = 'json', required = True)
        parser.add_argument('product_name', location = 'json', required = True)
        args = parser.parse_args()
        claim = get_jwt_claims()

        # Check the requirements
        if (
            args['to_number'] == '' or args['to_number'] is None
            or args['product_name'] == '' or args['product_name'] is None
        ):
            return {'message': 'Nomor tujuan dan nama produk harus diisi'}, 400
        
        # Get related user ID
        user = User.query.filter_by(username = claim['username']).first()
        user_id = user.id
        
        # Check whether the product exist or not (and belong to the right owner or not)
        product = Product.query.filter_by(user_id = user_id).filter_by(name = args['product_name']).first()
        if product is None:
            return {'message': 'Anda tidak memiliki produk bernama ' + args['product_name']}, 404
        
        # Generate OTP code
        otp_code = ''
        '''
        We generate random digit (0 - 9) six times. In each iteration we append it to otp_code, so in the end we will 
        get a random six digit code.
        '''
        for index in range(6):
            random_digit = random.randint(0, 9)
            random_digit = str(random_digit)
            otp_code += random_digit

        # Preparing some data needed before sending the otp code to related end-user
        product_id = product.id
        to_number = args['to_number']
        text_message = "Kode ini bersifat rahasia, jangan pernah memberitahukan kode ini kepada siapapun. "
        text_message += "Untuk melanjutkan proses, silahkan masukkan kode OTP berikut: " + otp_code

        # Send otp code to related end-user
        bulk_message_text.s(product_id, to_number, text_message, 'otp', datetime.now().strftime("%Y-%m-%d %H:%M:%S")).apply_async()

        # Send otp code to third party
        return {'to_number': to_number, 'otp_code': otp_code, 'message': 'Kode OTP telah dikirimkan ke user terkait'}, 200
    
# Endpoint in /otp route
api.add_resource(Otp, '')