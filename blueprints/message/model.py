# Import from standard libraries
from datetime import datetime, timedelta

# Import from related third party
from blueprints import db
from flask_restful import fields

# Import from other modules
from blueprints.product.model import Product

'''
The following class is used to make the model of "Message" table.
'''
class Message(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    uuid = db.Column(db.String(255), nullable = False, default = '')
    sender_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    from_number = db.Column(db.String(255), nullable = False)
    receiver = db.Column(db.String(255), nullable = False, default = '')
    to_number = db.Column(db.String(255), nullable = False, default = '')
    in_or_out = db.Column(db.String(3), nullable = False, default = 'out') # Values can be: in, out
    message_type = db.Column(db.String(255), nullable = False, default = 'text') # Values can be: text, image, file
    text_message = db.Column(db.Text, nullable = True, default = None)
    media_url = db.Column(db.String(255), nullable = True, default = None)
    caption = db.Column(db.String(255), nullable = True, default = None)
    status = db.Column(db.String(255), nullable = False, default = '')
    timestamp = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # The following dictionary is used to serialize "Message" instances into JSON form
    response_fields = {
        'id': fields.Integer,
        'uuid': fields.String,
        'sender_id': fields.Integer,
        'from_number': fields.String,
        'receiver': fields.String,
        'to_number': fields.String,
        'in_or_out': fields.String,
        'message_type': fields.String,
        'text_message': fields.String,
        'media_url': fields.String,
        'caption': fields.String,
        'status': fields.String,
        'timestamp': fields.String,
    }

    # Required fields when create new instances of "Message" class
    def __init__(
        self, uuid, sender_id, from_number, receiver, to_number, in_or_out, message_type, text_message, media_url, caption, status, timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ):
        self.uuid = uuid
        self.sender_id = sender_id
        self.from_number = from_number
        self.receiver = receiver
        self.to_number = to_number
        self.in_or_out = in_or_out
        self.message_type = message_type
        self.text_message = text_message
        self.media_url = media_url
        self.caption = caption
        self.status = status
        self.timestamp = timestamp
        
    # Reprsentative form to be shown in log
    def __repr__(self):
        return "UUID : " + self.uuid