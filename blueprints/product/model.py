# Import from standard libraries
from datetime import datetime, timedelta

# Import from related third party
from blueprints import db
from flask_restful import fields

# Import from other modules
from blueprints.user.model import User

'''
The following class is used to make the model of "Product" table.
'''
class Product(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    name = db.Column(db.String(255), nullable = False, default = '')
    phone_number = db.Column(db.String(255), nullable = False, default = '')
    api_key = db.Column(db.String(255), nullable = False, default = '')
    created_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # The following dictionary is used to serialize "Product" instances into JSON form
    response_fields = {
        'id': fields.Integer,
        'user_id': fields.Integer,
        'name': fields.String,
        'phone_number': fields.String,
        'api_key': fields.String,
        'created_at': fields.DateTime,
    }

    # Required fields when create new instances of "Product" class
    def __init__(
        self, user_id, name, phone_number, api_key
    ):
        self.user_id = user_id
        self.name = name
        self.phone_number = phone_number
        self.api_key = api_key
        
    # Reprsentative form to be shown in log
    def __repr__(self):
        return "ID : " + str(self.id)