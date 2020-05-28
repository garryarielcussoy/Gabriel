# Import from standard libraries
from datetime import datetime, timedelta

# Import from related third party
from blueprints import db
from flask_restful import fields

'''
The following class is used to make the model of "User" table.
'''
class User(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String(255), nullable = False, default = '')
    username = db.Column(db.String(255), nullable = False, default = '', unique = True)
    password = db.Column(db.String(255), nullable = False, default = '')
    created_at = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # The following dictionary is used to serialize "User" instances into JSON form
    response_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'username': fields.String,
        'password': fields.String,
        'created_at': fields.DateTime,
    }

    # Required fields when create new instances of "User" class
    def __init__(
        self, name, username, password
    ):
        self.name = name
        self.username = username
        self.password = password
        
    # Reprsentative form to be shown in log
    def __repr__(self):
        return "Username : " + self.username