import json
import pytest
import hashlib
from . import create_token,client, reset_db

from flask import Flask, request
from unittest import mock
from unittest.mock import patch
from unittest import TestCase
from blueprints.message.tasks import send_message_text,send_message_image,send_message_file
import requests 
import unittest
from datetime import datetime,timedelta
#Mocking Nexmo API


class TestNexmo():

    @mock.patch('blueprints.message.resources.send_message_text', return_value={"message_uuid": "api-text-002"})
    def test_post_text_nexmo(self,mock_send_message_text, client):
   
        reset_db()
        data={
            'sender_id':1,
            'to_number':'6285659229599',
            'message_type':'text',
            'text_message':"unit test"
        }
        res=client.post('/message',
        json=data,
        content_type='application/json')
 
        assert res.status_code==200

    @mock.patch('blueprints.message.resources.send_message_image', return_value={"message_uuid": "api-image-003"})
    def test_post_image_nexmo(self,mock_send_message_image, client):

        data={
            'sender_id':1,
            'to_number':'6285659229599',
            'message_type':'image',
            'media_url':"contoh_url",
            "caption":"ujicoba.jpg"
        }
        res=client.post('/message',
        json=data,
        content_type='application/json')

        assert res.status_code==200
    
    @mock.patch('blueprints.message.resources.send_message_file', return_value={"message_uuid": "api-file-004"})
    def test_post_file_nexmo(self,mock_send_message_file, client):

        data={
            'sender_id':1,
            'to_number':'6285659229599',
            'message_type':'file',
            'media_url':"contoh_url",
            "caption":"ujicoba.pdf"
        }
        res=client.post('/message',
        json=data,
        content_type='application/json')
  
        assert res.status_code==200

    def test_options_nexmo(self,client):
        res=client.options("/message", content_type="application/json")

        assert res.status_code==200

class TestStatus():
    def test_callback_status(self,client):
        data={
                "message_uuid": "api-text-002",
                "to": {
                    "type": "whatsapp",
                    "id": "6285659229599",
                    "number": "6285659229599"
                },
                "from": {
                    "type": "whatsapp",
                    "id": "0123456789012345",
                    "number": "14157386170"
                },
                "timestamp": "2020-01-01T14:00:00.000Z",
                "status": "delivered",
                "error": {
                    "code": 1300,
                    "reason": "Not part of the provider network"
                },
                "usage": {
                    "currency": "EUR",
                    "price": "0.0333"
                },
                "client_ref": "my-personal-reference"
        }
        res=client.post('/message/status',
        json=data,
        content_type='application/json')
  
        assert res.status_code==200

    def test_options_nexmo(self,client):
        res=client.options("/message/status", content_type="application/json")

        assert res.status_code==200


def mock_post_request(*args, **kwargs):
    class MockResponse():
        def __init__(self, json_data, status_code):
            self.json_data=json_data
            self.status_code=status_code
        
        def json(self):
            return self.json_data
    if args[0]=='https://messages-sandbox.nexmo.com/v0.1/messages':
        return MockResponse({'message_uuid':"api-TEST-015"},200)

class TestExternalRequest():
    @mock.patch('requests.post', side_effect=mock_post_request)
    def test_send_message_text(self, mock_post):
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response=send_message_text(1,'14157386170',"Bambang","6285659229599","UNIT TEST","out",date)
        assert response=='api-TEST-015'

    
    @mock.patch('requests.post', side_effect=mock_post_request)
    def test_send_message_image(self, mock_post):
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response=send_message_image(1,'14157386170',"Bambang", "6285659229599","image_url","example of image URL","out",date)
        assert response=='api-TEST-015'

    @mock.patch('requests.post', side_effect=mock_post_request)
    def test_send_message_file(self, mock_post):
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response=send_message_file(1,'14157386170',"Bambang", "6285659229599","file_url","example of file URL","out",date)
        assert response=='api-TEST-015'

