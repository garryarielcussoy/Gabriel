# Import from standard libraries
import json
import os
import requests
from datetime import timedelta, datetime

# from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_cors import CORS
from celery import Celery
from blueprints import app, db

# Import models
from blueprints.user.model import User
from blueprints.message.model import Message
from blueprints.product.model import Product

# Setup and initialize Celery
app.config['CELERY_BROKER_URL'] = 'amqp://garry:alterra123@localhost:5672/celery_test'
# app.config['CELERY_BROKER_URL'] = 'amqp://guest@localhost:5672/celery_WA'
app.config['CELERY_ALWAYS_EAGER'] = True
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

'''
The following function is used to bulk messaging of text type in background process

:param string product_id: ID of a product from a company (third party)
:param string to_number: Phone number of receiver
:param string text_message: The message of type text which will be sent to receiver
:param string indicator: Variable which indicates general or otp type message
:param string receiver: Name of the receiver
'''
@celery.task(name = "bulk_message_text")
def bulk_message_text(product_id, to_number, text_message, indicator = 'general', receiver = ''):
    # Get related product and auth key
    product = Product.query.filter_by(id = product_id).first()
    sender_id = product.id
    from_number = product.phone_number
    api_key = product.api_key

    # Formatting api key
    api_key_list = api_key.split(":")
    left_part = api_key_list[0]
    right_part = api_key_list[1]
    auth = (left_part, right_part)

    # Preparing some requirements needed to send the message
    url = 'https://messages-sandbox.nexmo.com/v0.1/messages'
    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    text_message = '[' + product.name + '] ' + text_message 

    # Compose the message
    data = {
        'from': {'type': 'whatsapp', 'number': from_number},
        'to': {'type': 'whatsapp', 'number': to_number},
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
    Store the record to database
    '''
    # Get message UUID and status
    uuid = 'Error'
    status = 'sent'
    json_response = response.json()
    if 'message_uuid' in json_response:
        uuid = json_response['message_uuid']
    else:
        status = 'failed'

    # Removing OTP code from the text before store it to database (for OTP message only)
    if indicator == 'otp':
        text_message = text_message[:-6] + '******'
    
    # Create new instance of message object
    new_message = Message(
        uuid = uuid,
        sender_id = sender_id,
        from_number = from_number,
        receiver = receiver,
        to_number = to_number,
        in_or_out = 'out',
        message_type = 'text',
        text_message = text_message,
        media_url = None,
        caption = None,
        status = status
    )

    # Store new record into database
    db.session.add(new_message)
    db.session.commit()

    # Return the UUID
    return {'uuid': uuid}

'''
The following function is used to bulk messaging of image type in background process

:param string product_id: ID of a product from a company (third party)
:param string to_number: Phone number of receiver
:param string media_url: Image url where the image (which will be sent to receiver) lies
:param string caption: Caption of the image
:param string receiver: Name of the receiver
'''
@celery.task(name = "bulk_message_image")
def bulk_message_image(product_id, to_number, media_url, caption, receiver = ''):
    # Get related product and auth key
    product = Product.query.filter_by(id = product_id).first()
    sender_id = product.id
    from_number = product.phone_number
    api_key = product.api_key

    # Formatting api key
    api_key_list = api_key.split(":")
    left_part = api_key_list[0]
    right_part = api_key_list[1]
    auth = (left_part, right_part)

    # Preparing some requirements needed to send the message
    url = 'https://messages-sandbox.nexmo.com/v0.1/messages'
    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    caption = '[' + product.name + '] ' + caption

    # Compose the message
    data = {
        'from': {'type': 'whatsapp', 'number': from_number},
        'to': {'type': 'whatsapp', 'number': to_number},
        'message': {
            'content': {
                'type': 'image',
                'image': {
                    'url': media_url,
                    'caption': caption
                }
            }
        }
    }

    # Turn json dictionary into json string
    data = json.dumps(data)

    # Send the message
    response = requests.post(url, data = data, headers = header, auth = auth)

    '''
    Store the record to database
    '''
    # Get message UUID and status
    uuid = 'Error'
    status = 'sent'
    json_response = response.json()
    if 'message_uuid' in json_response:
        uuid = json_response['message_uuid']
    else:
        status = 'failed'
    
    # Create new instance of message object
    new_message = Message(
        uuid = uuid,
        sender_id = sender_id,
        from_number = from_number,
        receiver = receiver,
        to_number = to_number,
        in_or_out = 'out',
        message_type = 'image',
        text_message = None,
        media_url = media_url,
        caption = caption,
        status = 'sent'
    )

    # Store new record into database
    db.session.add(new_message)
    db.session.commit()

    # Return the UUID
    return {'uuid': uuid}

'''
The following function is used to bulk messaging of file type in background process

:param string product_id: ID of a product from a company (third party)
:param string to_number: Phone number of receiver
:param string media_url: File url where the file (which will be sent to receiver) lies
:param string caption: Caption of the file
:param string receiver: Name of the receiver
'''
@celery.task(name = "bulk_message_file")
def bulk_message_file(product_id, to_number, media_url, caption, receiver = ''):
    # Get related product and auth key
    product = Product.query.filter_by(id = product_id).first()
    sender_id = product.id
    from_number = product.phone_number
    api_key = product.api_key

    # Formatting api key
    api_key_list = api_key.split(":")
    left_part = api_key_list[0]
    right_part = api_key_list[1]
    auth = (left_part, right_part)

    # Preparing some requirements needed to send the message
    url = 'https://messages-sandbox.nexmo.com/v0.1/messages'
    header = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    caption = '[' + product.name + '] ' + caption

    # Compose the message
    data = {
        'from': {'type': 'whatsapp', 'number': from_number},
        'to': {'type': 'whatsapp', 'number': to_number},
        'message': {
            'content': {
                'type': 'image',
                'image': {
                    'url': media_url,
                    'caption': caption
                }
            }
        }
    }

    # Turn json dictionary into json string
    data = json.dumps(data)

    # Send the message
    response = requests.post(url, data = data, headers = header, auth = auth)

    '''
    Store the record to database
    '''
    # Get message UUID and status
    uuid = 'Error'
    status = 'sent'
    json_response = response.json()
    if 'message_uuid' in json_response:
        uuid = json_response['message_uuid']
    else:
        status = 'failed'
    
    # Create new instance of message object
    new_message = Message(
        uuid = uuid,
        sender_id = sender_id,
        from_number = from_number,
        receiver = receiver,
        to_number = to_number,
        in_or_out = 'out',
        message_type = 'file',
        text_message = None,
        media_url = media_url,
        caption = caption,
        status = 'sent'
    )

    # Store new record into database
    db.session.add(new_message)
    db.session.commit()

    # Return the UUID
    return {'uuid': uuid}