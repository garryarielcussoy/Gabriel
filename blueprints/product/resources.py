from flask import Blueprint
from flask_restful import marshal,Resource,reqparse,Api
from flask_jwt_extended import create_access_token,get_jwt_claims,get_jwt_identity, jwt_required
from blueprints.product.model import Product
from blueprints import db, app

bp_product=Blueprint('product', __name__)
api=Api(bp_product)


'''This part enable all registered user to add and get their product list from database'''
class AddProduct(Resource):
    def options(self):
        return 200
    
    #Add product by user
    @jwt_required
    def post(self):
        
        parser=reqparse.RequestParser()
        parser.add_argument('user_id', location='json')
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('phone_number', location='json')
        parser.add_argument('api_key', location='json', default="tchOyRAB5oEtSrBW")
        args=parser.parse_args()

        #Only getting data query which is associated with user id
        user_id=get_jwt_claims()['data']['id']

        check_product=Product.query.filter_by(name=args['name'])
        if check_product is not None:
            return {'status':'Produk Sudah Ada Di Data Kami'},403

        new_product=Product(user_id, args['name'], args['phone_number'], args['api_key'])
        #push to Product Table in Database
        db.session.add(new_product)
        db.session.commit()

        return {'status':'Produk Berhasil Ditambahkan'},200
    
    #Get products query by user

    @jwt_required
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('p', location='args', type=int,default=1)  
        parser.add_argument('rp', location='args', type=int, default=25)
        args=parser.parse_args()
        get_history= Product.query.filter_by(user_id=get_jwt_claims()['data']['id'])
        
        if get_history == None:
            return {'status': 'Data Tidak Ditemukan'}, 403
        offset=(args['p']*args['rp'])-args['rp']
        #looping all quaery to provide list of products
        rows=[]
        for row in get_history.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Product.response_fields))
        return rows, 200
    
    
#ENDPOINTS

api.add_resource(AddProduct,'')
