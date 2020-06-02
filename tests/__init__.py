import pytest, json, logging
from app import app
from flask import Flask, request
import hashlib
from blueprints import db,app
from blueprints.user.model import User
from blueprints.product.model import Product

def reset_db():
    db.drop_all()
    db.create_all()
    encrypted_pass=hashlib.md5('shopee'.encode()).hexdigest()
    user=User("Shopee","shopee",encrypted_pass)
    product=Product(1,"ShopeePay","628777777","api-key-0001")

    db.session.add(user)
    db.session.commit()

    db.session.add(product)
    db.session.commit()

@pytest.fixture
def client(request):
    return app.test_client(request)

def create_token(isInternal=True):
    data=[]
    if isInternal:
        data.append({
            'username':"admin",
            'password':"admin"
        })
    else:
         data.append({
            'username':"shopee",
            'password':"shopee"
        })
    
    req= app.test_client(request)
    res= req.post('/login', json=data[0])
    res_json=json.loads(res.data)
    logging.warning("Result:%s",res_json)

    if res.status_code==200:
        assert res.status_code==200
        return res_json['token']
    else:
        pass

