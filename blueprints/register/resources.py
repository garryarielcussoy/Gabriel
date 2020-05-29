# Import from standard libraries
import json
import hashlib

# Import from related third party
from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims

# Import model
from blueprints.user.model import User
from blueprints import app,db


# Creating blueprint
bp_register = Blueprint('register', __name__)
api = Api(bp_register)

class Register(Resource):
    def options(self):
        return 200

    def post(self):
        #fields for new user to be added in User Table
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json',required=True)
        parser.add_argument('username', location = 'json', required = True)
        parser.add_argument('password', location = 'json', required = True)
        args = parser.parse_args()
        
        hidden_password=hashlib.md5(args['password'].encode()).hexdigest()
        check_username=User.query.filter_by(username=args['username']).first()

        if args['name'] is None or args['username'] is None or args['password'] is  None:
            return {'status':'Tidak Boleh Ada Kolom Yang Kosong'},403
        elif check_username is not None:
            return {'status':'Username Yang Anda Masukan Sudah Terpakai'},404

        new_user=User(args['name'], args['username'], hidden_password)
        db.session.add(new_user)
        db.session.commit()

        return {'status':'Pendaftaran Berhasil, Silakan Login'}, 200

#ENPOINT Register
api.add_resource(Register,'')
