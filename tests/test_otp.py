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
The following class is defined to test each scenarion related to OTP process
'''
class TestOtp():
    # OTP with missing required arguments
    def test_otp_missing_req(self, client):
        # Prepare DB and token
        reset_db()
        token = create_token(False)
        
        # Prepare some data neeeded
        data = {
            'to_number': '6285659229599',
            'product_name': ''
        }
        headers = {
            'Authorization': 'Bearer ' + token
        }

        # Hit related endpoint and get the response
        res = client.post('/otp', json = data, headers = headers, content_type = 'application/json')
        json_res = json.loads(res.data)
 
        # Testing the response
        assert res.status_code == 400
        assert json_res['message'] == 'Nomor tujuan dan nama produk harus diisi'
    
    # OTP process failed because poduct name doesn't exist
    def test_otp_product_not_exist(self, client):
        # Prepare DB and token
        reset_db()
        token = create_token(False)
        
        # Prepare some data neeeded
        data = {
            'to_number': '6285659229599',
            'product_name': 'Shopee'
        }
        headers = {
            'Authorization': 'Bearer ' + token
        }

        # Hit related endpoint and get the response
        res = client.post('/otp', json = data, headers = headers, content_type = 'application/json')
        json_res = json.loads(res.data)
 
        # Testing the response
        assert res.status_code == 404
        assert json_res['message'] == 'Anda tidak memiliki produk bernama Shopee'
    
    # Test OTP process that ended successfully
    def test_otp_success(self, client):
        # Prepare DB and token
        reset_db()
        token = create_token(False)
        
        # Prepare some data neeeded
        data = {
            'to_number': '6285659229599',
            'product_name': 'ShopeePay'
        }
        headers = {
            'Authorization': 'Bearer ' + token
        }

        # Hit related endpoint and get the response
        res = client.post('/otp', json = data, headers = headers, content_type = 'application/json')
        json_res = json.loads(res.data)
 
        # Testing the response
        assert res.status_code == 200
        assert json_res['message'] == 'Kode OTP telah dikirimkan ke user terkait'
    
    # Test options endpoint in otp
    def test_options_otp(self, client):
        # Prepare DB and token
        reset_db()

        # Hit related endpoint and get the response
        res = client.options('/otp')
        json_res = json.loads(res.data)
 
        # Testing the response
        assert res.status_code == 200
        assert json_res['status'] == 'ok'