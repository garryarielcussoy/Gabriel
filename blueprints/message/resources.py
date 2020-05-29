from flask import Blueprint,request,render_template,Flask
from flask_restful import reqparse,Api, Resource,marshal
from blueprints import db
from flask_jwt_extended import jwt_required,create_access_token, get_jwt_claims, get_jwt_identity
import requests
import json
from .model import Message

##Import packages for celery tasks
from .tasks import send_message_file,send_message_image,send_message_text,callback
from celery import Celery 
from datetime import datetime,timedelta

bp_message=Blueprint("message", __name__)
api=Api(bp_message)

###CRUD METHODS


class MessageOne(Resource):
    def __init__(self):
        pass
    @jwt_required
    def post(self):
        ##Creates Arguments Imput Using JSON BODY
        parser=reqparse.RequestParser()
        parser.add_argument('sender_id', location='json', required=True)
        parser.add_argument('from_number', location='json')
        parser.add_argument('receiver', location='json', default="None")
        parser.add_argument('to_number', location='json', required=True)
        parser.add_argument('in_or_out', location='json',default='out')
        parser.add_argument('message_type', location='json', required=True)
        parser.add_argument('text_message', location='json', default='None')
        parser.add_argument('media_url', location='json', default='None')
        parser.add_argument('caption', location='json', default='None')
        parser.add_argument('status', location='json', default='ON PROCESS')
        parser.add_argument('timestamp', location='json', default='ON PROCESS')
        
        args=parser.parse_args()
        
        '''Identifying the type of messages [text, image, or  file] and executes differently 
           based on its type'''

      

        if args['message_type']=='text':
            send_message_text.s(args['sender_id'],args['receiver'],args['to_number'], args['text_message'], args['in_or_out']).apply_async()
 
        elif args['message_type']=='image':
            if args['media_url']=='None':
                return {'status':'Media URL Cannot Be Empty'}, 404
            else:
                send_message_image.s(args['sender_id'],args['receiver'],args['to_number'], args['media_url'],args['caption'], args['in_or_out']).apply_async()
        elif args['message_type']=='file':
            if args['media_url']=='None':
                return {'status':'Media URL Cannot Be Empty'}, 404
            else:
                send_message_file.s(args['sender_id'],args['receiver'],args['to_number'], args['media_url'],args['caption'], args['in_or_out']).apply_async()

        return {'status':"Terkirim"},200


    def options(self):
        return 200

##Receive Callback Response For Every Message Sent
class CallbackMsg(Resource):
    def __init__(self):
        pass

    def options(self):
        return 200

    def post(self):
        #Get JSON Response from Nexmo API
        data=request.get_json()

        #Manage Its Response To Be More Scheduled & Easy To Be Monitored
        callback.apply_async(args=[data], retry=True, retry_policy={
            'max_retries':2,
            'interval_start':0,
            'interval_step':0,
            'interval_max':60,
        })
        return 200

#Get The History of All Messages Sent, Only Specific User Who Has Been Login Can Access 
class GetHistory(Resource):
    def options(self):
        return 200
    
    @get_jwt_claims
    def get(self):
        
        parser=reqparse.RequestParser()
        parser.add_argument('p', location='args', type=int,default=1)  
        parser.add_argument('rp', location='args', type=int, default=25)
        args=parser.parse_args()

        get_history= Message.query.filter_by(from_number='14157386170')
        
        if get_history == None:
            return {'status': 'Data Tidak Ditemukan'}, 403

        offset=(args['p']*args['rp'])-args['rp']
        #looping all quaery to provide list of products
        rows=[]
        for row in get_history.order_by(Message.timestamp.desc()).offset(offset).limit(args['rp']).all():
            rows.append(marshal(row, Message.response_fields))
        return rows, 200
    

    
class GetById(Resource):
    @get_jwt_claims
    def get(self,uuid):
        parser=reqparse.RequestParser()
        parser.add_argument('p', location='args', type=int,default=1)  
        parser.add_argument('rp', location='args', type=int, default=25)
        args=parser.parse_args()
        get_history= Message.query.filter_by(uuid=uuid)
        
        if get_history == None:
            return {'status': 'Data Tidak Ditemukan'}, 403
        offset=(args['p']*args['rp'])-args['rp']
        #looping all quaery to provide list of products
        rows=[]
        for row in get_history.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Message.response_fields))
        return rows, 200

    
class GetByNum(Resource):
    @get_jwt_claims
    def get(self,phone_num):
        parser=reqparse.RequestParser()
        parser.add_argument('p', location='args', type=int,default=1)  
        parser.add_argument('rp', location='args', type=int, default=25)
        args=parser.parse_args()
        get_history= Message.query.filter_by(to_number="{}".format(phone_num))
        
        if get_history == None:
            return {'status': 'Data Tidak Ditemukan'}, 403
        offset=(args['p']*args['rp'])-args['rp']
        #looping all quaery to provide list of products
        rows=[]
        for row in get_history.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Message.response_fields))
        return rows, 200

###ENPOINTS
api.add_resource(MessageOne, '')
api.add_resource(CallbackMsg, '/status')
api.add_resource(GetHistory, '/history')
api.add_resource(GetById, '/history/id/<string:uuid>')
api.add_resource(GetByNum, '/history/num/<int:phone_num>')