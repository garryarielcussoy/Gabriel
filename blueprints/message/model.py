# Import from standard libraries
from datetime import datetime, timedelta

# Import from related third party
from blueprints import db
from flask_restful import fields

'''
The following class is used to make the model of "Message" table.
'''
class Message(db.Model):
    # Define the property (each property associated with a column in database)
    __tablename__ = 'message'
    uuid = db.Column(db.String(255), primary_key = True, nullable = False)
    from_number = db.Column(db.String(255), nullable = False)
    to_number = db.Column(db.String(255), nullable = False, default = '')
    in_or_out = db.Column(db.String(3), nullable = False, default = 'out') # Values can be: in, out
    message_type = db.Column(db.String(255), nullable = False, default = 'text') # Values can be: text, image, file
    text_message = db.Column(db.Text, nullable = False, default = '')
    media_url = db.Column(db.String(255), nullable = False, default = '')
    caption = db.Column(db.String(255), nullable = False, default = '')
    status = db.Column(db.String(255), nullable = False, default = '')
    timestamp = db.Column(db.DateTime, default = datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # The following dictionary is used to serialize "Message" instances into JSON form
    response_fields = {
        'uuid': fields.String,
        'from_number': fields.String,
        'to_number': fields.String,
        'in_or_out': fields.String,
        'message_type': fields.String,
        'text_message': fields.String,
        'media_url': fields.String,
        'caption': fields.String,
        'status': fields.String,
        'created_at': fields.DateTime,
    }

    # Required fields when create new instances of "Message" class
    def __init__(
        self, uuid, from_number, to_number, in_or_out, message_type, text_message, media_url, caption, status
    ):
        self.uuid = uuid
        self.from_number = from_number
        self.to_number = to_number
        self.in_or_out = in_or_out
        self.message_type = message_type
        self.media_url = media_url
        self.caption = caption
        self.status = status
        
    # Reprsentative form to be shown in log
    def __repr__(self):
        return "UUID : " + self.uuid