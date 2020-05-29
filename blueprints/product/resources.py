from flask import Blueprint
from flask_restful import marshal,Resource,reqparse,Api
from flask_jwt_extended import create_access_token,get_jwt_claims,get_jwt_identity, jwt_required
from blueprints.product.model import Product
from blueprints import db, app

class AddProduct(Resource):
    def options(self):
        return 200
    
    @jwt_required
    def post(self):
        parser=reqparse.RequestParser()
        parser.add_argument('user_id', location='json')
        parser.add_argument('name', location='json')
        parser.add_argument('phone_number', location='json')
        parser.add_argument('api_key', location='json', default="tchOyRAB5oEtSrBW")
        args=parser.parse_args()
        
        user_id=get_jwt_claims()['data']['id']

        check_product=Product.query.filter_by(name=args['name'])
        if check_product is not None:
            return {'status':'Produk Sudah Ada Di Data Kami'},403

        new_product=Product(user_id, args['name'], args['phone_number'], args['api_key'])

        db.session.add(new_product)
        db.session.commit()

        return {'status':'Produk Berhasil Ditambahkan'},200
    
    def get(self):

    

