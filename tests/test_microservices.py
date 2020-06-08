import json
from . import client,create_token, reset_db
import unittest
from flask import request,Flask

class TestRegister():
    def test_post_register_new_user(self,client):
        data={
            'name':"saya",
            'username':"saya",
            'password':"passwords"
        }
        res=client.post('/register',
        json=data,
        content_type='application/json')
 
        assert res.status_code==200

    def test_options_register(self,client):
        res=client.options('/register',
        content_type='application/json')
 
        assert res.status_code==200



class TestLogin():
    def test_post_login(self,client):
     
        data={
            'username':"saya",
            'password':"passwords"
        }
        res=client.post('/login',
        json=data,
        content_type='application/json')
        
        assert res.status_code==200
    
    def test_options_login(self,client):
        res=client.options('/login',
        content_type='application/json')
        
        assert res.status_code==200


class TestHistory():
    def test_get_history_all(self,client):
        token=create_token(False)

        res=client.get("/message/history", 
        headers={'Authorization':'Bearer ' + token},
        content_type="application/json")
        
        assert res.status_code==200

    def test_get_history_by_uuid(self,client):
        token=create_token(False)

        res=client.get("/message/history/id/api-text-002", 
        headers={'Authorization':'Bearer ' + token},
        content_type="application/json")

        assert res.status_code==200

    def test_get_history_by_phone_num(self,client):
        token=create_token(False)

        res=client.get("/message/history/num/6285659229599",
        headers={'Authorization':'Bearer ' + token},
        content_type="application/json")

        assert res.status_code==200
    
    def test_options_history(self,client):
        res=client.options("/message/history", content_type="application/json")

        assert res.status_code==200

class TestProduct():
    def test_post_product(self,client):
        token=create_token(False)
        data={
            'name':"Tanam",
            'phone_number':"0777777568"
            
        }
        res=client.post('/product',
        headers={'Authorization':'Bearer ' + token},
        json=data,
        content_type="application/json")

        assert res.status_code==200
    
    def test_get_product(self,client):
        token=create_token(False)

        res=client.get('/product',
        headers={'Authorization':'Bearer ' + token},
        content_type="application/json")

        assert res.status_code==200

    def test_update_product(self,client):
        token=create_token(False)

        data={
            'name':"Tanam Dari Shopee",
            'phone_number':"077777755677",
            'api_key':"ooooo-pppp"

        }

        res=client.put('/product/1',
        headers={'Authorization':'Bearer ' + token},
        json=data,
        content_type="application/json")

        assert res.status_code==200

    def test_options_product(self,client):
        token=create_token(False)

        res=client.options('/product',
        headers={'Authorization':'Bearer ' + token},
        content_type="application/json")

        assert res.status_code==200






    

