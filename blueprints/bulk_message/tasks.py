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

:param string receiver: Phone number of receiver
:param string text_message: The message of type text which will be sent to receiver
'''
@celery.task(name = "bulk_message_text")
def bulk_message_text(receiver, text_message):
    # Preparing some requirements needed to send the message
    url = 'https://messages-sandbox.nexmo.com/v0.1/messages'
    sender = "14157386170"
    auth = ('8fe08f4c', 'Mz1oxyxiDZoicksE')
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
    
    # Create new instance of message object

'''
The following function is used to bulk messaging of image type in background process

:param string receiver: Phone number of receiver
:param string media_url: Image url where the image (which will be sent to receiver) lies
:param string caption: Caption of the image
'''
@celery.task(name = "bulk_message_image")
def bulk_message_image(receiver, media_url, caption):
    # Preparing some requirements needed to send the message
    url = 'https://messages-sandbox.nexmo.com/v0.1/messages'
    sender = "14157386170"
    auth = ('8fe08f4c', 'Mz1oxyxiDZoicksE')
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
The following function is used to bulk messaging of file type in background process

:param string receiver: Phone number of receiver
:param string media_url: File url where the file (which will be sent to receiver) lies
:param string caption: Caption of the file
'''
@celery.task(name = "bulk_message_file")
def bulk_message_file(receiver, media_url, caption):
    # Preparing some requirements needed to send the message
    url = 'https://messages-sandbox.nexmo.com/v0.1/messages'
    sender = "14157386170"
    auth = ('8fe08f4c', 'Mz1oxyxiDZoicksE')
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