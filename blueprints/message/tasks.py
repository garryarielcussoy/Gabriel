from celery import Celery
from flask import Blueprint,request,render_template,Flask
from flask_restful import reqparse,Api, Resource,marshal
from blueprints import app,db

from flask_jwt_extended import jwt_required,create_access_token, get_jwt_claims, get_jwt_identity
import requests
import json
from .model import Message


# Setup and initialize Celery
app.config['CELERY_BROKER_URL'] = 'amqp://guest:guest@localhost:5672/celery_WA'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

###Prepare Access For External API Requirements
nexmo_host="https://messages-sandbox.nexmo.com/v0.1/messages"
secret_key='299a3afd'
sender='14157386170'
api_key='tchOyRAB5oEtSrBW'
headers={
    'Content-Type':'application/json',
    'Accept':'application/json'
}

''' All input for variabel "data" below must be in string format
    -params receiver: contains number of receiver of message, must be start by country code
                     without "+" sign
    -params text_message: contains the text body to be sent away to receiver
    -params in_out: regarding the message is to be carried out ("out")to receiver or the sender 
                    received it from other ("in"), Default is set to be "out"
'''

@celery.task(name="send_message_text")
def send_message_text(receiver, text_message, in_out):
    data='''{
            "from":{ "type": "whatsapp", "number": "%s" },
            "to": { "type": "whatsapp", "number": "%s" },
            "message": {"content": 
            {"type": "text",
            "text": "%s"}}}'''%(sender,receiver,text_message)
     
    call_nexmo=requests.post(nexmo_host,headers=headers,data=data,auth=(secret_key,api_key))
    #Get the message_uuid or message id generated by NEXMO
    uuid=call_nexmo.json()['message_uuid']

    sent_msg= Message(uuid, sender,receiver, in_out, "text", text_message, "None", "None","ON PROCESS")
    #Push the data into designated Table in database
    db.session.add(sent_msg)
    db.session.commit()
    
'''
    -params receiver: contains number of receiver of message, must be start by country code
                     without "+" sign
    -params media_url: contains url of specific image to be sent away to receiver
    -params caption: contains name of image file. Sender can type it whatever they want 
    -params in_out: regarding the message is to be carried out ("out")to receiver or the sender 
                    received it from other ("in"), Default is set to be "out"
'''
@celery.task(name="send_message_image")
def send_message_image(receiver, media_url, caption, in_out):
    data='''{
            "from":{ "type": "whatsapp", "number": "%s" },
            "to": { "type": "whatsapp", "number": "%s" },
            "message": {"content": 
            {"type": "image",
            "image":{
                "url":"%s",
                "caption":"%s"}
            }}}'''%(sender,receiver, media_url, caption)
      
    call_nexmo=requests.post(nexmo_host,headers=headers,data=data,auth=(secret_key,api_key))
     #Get the message_uuid or message id generated by NEXMO
    uuid=call_nexmo.json()['message_uuid']
    sent_msg= Message(uuid,sender,receiver,in_out,"image","None", media_url, caption,"ON PROCESS")
    #Push data into designated Table in database
    db.session.add(sent_msg)
    db.session.commit()

'''
    -params receiver: contains number of receiver of message, must be start by country code
                     without "+" sign
    -params media_url: contains url of specific file to be sent away to receiver
    -params caption: contains name of file. Sender can type it whatever they want 
    -params in_out: regarding the message is to be carried out ("out")to receiver or the sender 
                    received it from other ("in"), Default is set to be "out"
'''

@celery.task(name="send_message_file")
def send_message_file(receiver, media_url, caption, in_out):
    data='''{
            "from":{ "type": "whatsapp", "number": "%s" },
            "to": { "type": "whatsapp", "number": "%s" },
            "message": {"content": 
            {"type": "file",
            "file":{
                "url":"%s",
                "caption":"%s"}
            }}}'''%(sender, receiver,media_url, caption)

    call_nexmo=requests.post(nexmo_host,headers=headers,data=data,auth=(secret_key,api_key))
    uuid=call_nexmo.json()['message_uuid']
    sent_msg= Message(uuid,sender,receiver,in_out,"file","None", media_url, caption,"ON PROCESS")
    db.session.add(sent_msg)
    db.session.commit()

'''-params data: contains callbcak response from Nexmo about message_uuid and status of message
                 [submitted','rejected','delivered','read']. ON PROCESS status is default from 
                 database that we created
'''
@celery.task(name="callback")
def callback(data):
    find_status=Message.query.filter_by(uuid=data['message_uuid']).first()
    
    if find_status is None:
        return {'status':'Message UUID Not Found'},404
    else:
         #Update message status in designated Table in database
        find_status.status= data['status']
   
    db.session.commit()
    