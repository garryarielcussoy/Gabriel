# Import standard libraries
import json
import hashlib
import requests

# Import related third parties
from flask import Flask, request
from unittest import mock
from unittest.mock import patch
from unittest import TestCase
import pytest 
import unittest

# Import from other modules
from blueprints.bulk_message.tasks import bulk_message_text, bulk_message_image, bulk_message_file
from . import create_token, client, reset_db

'''
The following class is defined to test the process of bulk messaging
'''
class TestBulkMessage():
    # Test the case when CSV file doesn't exist
    def test_bulk_missing_csv(self, client):
        # Prepare DB and token
        reset_db()
        token = create_token(False)
        
        # Prepare some data neeeded
        data = {
            'csv_file': []
        }
        headers = {
            'Authorization': 'Bearer ' + token
        }

        # Hit related endpoint and get the response
        res = client.post('/message_bulk', json = data, headers = headers, content_type = 'application/json')
        json_res = json.loads(res.data)
 
        # Testing the response
        assert res.status_code == 400
        assert json_res['message'] == 'Tidak ada file CSV / XLS yang diunggah'

    # Succesfully bulk messaging
    def test_bulk_success(self, client):
        # Prepare DB and token
        reset_db()
        token = create_token(False)
        
        # Prepare some data neeeded
        data = {
            'csv_file': [
                {
                    "type": "text",
                    "product_name": "Sepulsa.com",
                    "to_number": "6289514845202",
                    "receiver": "Garry",
                    "text_message": "Hello Garry!"
                },
                {
                    "type": "text",
                    "product_name": "ShopeePay",
                    "to_number": "6285719748157",
                    "receiver": "Daniel",
                    "text_message": "Hello Daniel!"
                },
                {
                    "type": "image",
                    "product_name": "Alterra Academy",
                    "to_number": "6289514845202",
                    "receiver": "Garry",
                    "media_url": "https://cdn.techinasia.com/data/images/3alC4cHrPwxaZLcHXaVdtIrdZg1AipfkSizMSAzL.jpeg",
                    "caption": "Logo Alterra"
                },
                {
                    "type": "image",
                    "product_name": "ShopeePay",
                    "to_number": "6285719748157",
                    "receiver": "Daniel",
                    "media_url": "https://cdn.techinasia.com/data/images/3alC4cHrPwxaZLcHXaVdtIrdZg1AipfkSizMSAzL.jpeg",
                    "caption": "Logo Alterra"
                },
                {
                    "type": "file",
                    "product_name": "ShopeePay",
                    "to_number": "6289514845202",
                    "receiver": "Garry",
                    "media_url": "https://cdn.techinasia.com/data/images/3alC4cHrPwxaZLcHXaVdtIrdZg1AipfkSizMSAzL.jpeg",
                    "caption": "File Berisi Logo Alterra"
                }
            ]
        }
        headers = {
            'Authorization': 'Bearer ' + token
        }

        # Hit related endpoint and get the response
        res = client.post('/message_bulk', json = data, headers = headers, content_type = 'application/json')
        json_res = json.loads(res.data)
 
        # Testing the response
        assert res.status_code == 200
        assert json_res['message'] == 'Sedang mengirim pesan'
    
    # Test options endpoint in bulk message
    def test_options_bulk(self, client):
        # Prepare DB and token
        reset_db()

        # Hit related endpoint and get the response
        res = client.options('/message_bulk')
        json_res = json.loads(res.data)
 
        # Testing the response
        assert res.status_code == 200
        assert json_res['status'] == 'ok'

# Define mock response that will be used as a replacement of Nexmo response
def mock_post_request(*args, **kwargs):
    class MockResponse():
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
        
        def json(self):
            return self.json_data

    if args[0] == 'https://messages-sandbox.nexmo.com/v0.1/messages':
        return MockResponse({'message_uuid': "api-TEST-047"}, 200)

class TestBulkMessageOnBackground():
    # Test bulk message of text type which have indicator 'general'
    @mock.patch('requests.post', side_effect = mock_post_request)
    def test_bulk_message_text_general(self, mock_post):
        # Hit related endpoint and get the response
        response = bulk_message_text(1, "6285659229599", "UNIT TEST", "general", "Bambang")

        # Testing the response
        assert response['uuid'] == 'api-TEST-047'

    # Test bulk message of text type which have indicator 'otp
    @mock.patch('requests.post', side_effect = mock_post_request)
    def test_bulk_message_text_otp(self, mock_post):
        # Hit related endpoint and get the response
        response = bulk_message_text(1, "6285659229599", "Kode Anda adalah: 123456", "otp", "Bambang")

        # Testing the response
        assert response['uuid'] == 'api-TEST-047'
    
    # Test bulk message of image type
    @mock.patch('requests.post', side_effect = mock_post_request)
    def test_bulk_message_image(self, mock_post):
        # Hit related endpoint and get the response
        response = bulk_message_image(1, "6285659229599", "http://image.com", "Gambar.com", "Bambang")

        # Testing the response
        assert response['uuid'] == 'api-TEST-047'
    
    # Test bulk message of file type
    @mock.patch('requests.post', side_effect = mock_post_request)
    def test_bulk_message_file(self, mock_post):
        # Hit related endpoint and get the response
        response = bulk_message_file(1, "6285659229599", "http://file.com", "File.com", "Bambang")

        # Testing the response
        assert response['uuid'] == 'api-TEST-047'