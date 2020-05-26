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

# Setup and initialize Celery
app.config['CELERY_BROKER_URL'] = 'amqp://garry:alterra123@localhost:5672/celery_test'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

'''
The following function is used to bulk messaging of text type in background process

:param string username: Username of related company (third party)
:param string receiver: Phone number of receiver
:param string text_message: The message of type text which will be sent to receiver
:param string indicator: Variable which indicates general or otp type message
'''
@celery.task(name = "bulk_message_text")
def bulk_message_text(username, receiver, text_message, indicator = 'general'):
    # Get sender phone number and auth key
    user = User.query.filter_by(username = username).first()
    sender = user.phone_number
    api_key = user.api_key

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
    Store the record to database
    '''
    # Get message UUID
    response = response.__dict__
    content = response['_content']
    content = content.decode('utf8') # Decode binary content
    json_response = json.loads(content) # Turn content into JSON format
    uuid = json_response['message_uuid']

    # Removing OTP code from the text before store it to database (for OTP message only)
    if indicator == 'otp':
        text_message = text_message[:-6] + '******'
    
    # Create new instance of message object
    new_message = Message(
        uuid = uuid,
        from_number = sender,
        to_number = receiver,
        in_or_out = 'out',
        message_type = 'text',
        text_message = text_message,
        media_url = None,
        caption = None,
        status = 'sent'
    )

    # Store new record into database
    db.session.add(new_message)
    db.session.commit()

'''
The following function is used to bulk messaging of image type in background process

:param string username: Username of related company (third party)
:param string receiver: Phone number of receiver
:param string media_url: Image url where the image (which will be sent to receiver) lies
:param string caption: Caption of the image
'''
@celery.task(name = "bulk_message_image")
def bulk_message_image(username, receiver, media_url, caption):
    # Get sender phone number and auth key
    user = User.query.filter_by(username = username).first()
    sender = user.phone_number
    api_key = user.api_key

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

    # Compose the message
    data = {
        'from': {'type': 'whatsapp', 'number': sender},
        'to': {'type': 'whatsapp', 'number': receiver},
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
    # Get message UUID
    response = response.__dict__
    content = response['_content']
    content = content.decode('utf8') # Decode binary content
    json_response = json.loads(content) # Turn content into JSON format
    uuid = json_response['message_uuid']
    
    # Create new instance of message object
    new_message = Message(
        uuid = uuid,
        from_number = sender,
        to_number = receiver,
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

'''
The following function is used to bulk messaging of file type in background process

:param string username: Username of related company (third party)
:param string receiver: Phone number of receiver
:param string media_url: File url where the file (which will be sent to receiver) lies
:param string caption: Caption of the file
'''
@celery.task(name = "bulk_message_file")
def bulk_message_file(username, receiver, media_url, caption):
    # Get sender phone number and auth key
    user = User.query.filter_by(username = username).first()
    sender = user.phone_number
    api_key = user.api_key

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

    # Compose the message
    data = {
        'from': {'type': 'whatsapp', 'number': sender},
        'to': {'type': 'whatsapp', 'number': receiver},
        'message': {
            'content': {
                'type': 'file',
                'file': {
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
    # Get message UUID
    response = response.__dict__
    content = response['_content']
    content = content.decode('utf8') # Decode binary content
    json_response = json.loads(content) # Turn content into JSON format
    uuid = json_response['message_uuid']
    
    # Create new instance of message object
    new_message = Message(
        uuid = uuid,
        from_number = sender,
        to_number = receiver,
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