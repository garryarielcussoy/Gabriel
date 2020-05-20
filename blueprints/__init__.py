# Import from standard libraries
import json
import os
from datetime import timedelta
from functools import wraps

# Import from related third party
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims, get_raw_jwt
from flask_cors import CORS

# A step to prevent CORS
app = Flask(__name__)
CORS(app)

# Set the following to true, if you want to auto-reload when there is a change, or false otherwise
app.config['APP_DEBUG'] = True

# JWT setup
app.config['JWT_SECRET_KEY'] = 'c2n!$st0pDo1ngt#!s$tuff'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days = 1)
jwt = JWTManager(app)

'''
The following function is designed as a decorator for admin authentication.
'''
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        
        # Validate username
        if claims['username'] == 'gabriel':
            return fn(*args, **kwargs)
        else:
            return {'message': 'Restricted! Admin Only'}, 403
    return wrapper

# ---------- Database Setup ----------
# Connect to database
try:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:alterra123@localhost:3306/gabriel'    
except Exception as e:
    raise e

# Set some environment variable related to database things
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_url = os.getenv('DB_URL')
db_selected = os.getenv('DB_SELECTED')

# Setup database migration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
# ---------- End of database setup ----------

# Import modules related to routing

# Register routes

# Create the database
db.create_all()

'''
Handle response from a request
'''
@app.after_request
def after_request(response):
    try:
        request_data = response.get_json()
    except Exception as e:
        request_data = response.args.to_dict()
    
    log_data = json.dumps({
        'status_code': response.status_code,
        'method': request.method,
        'code': response.status,
        'uri': request.full_path,
        'requedatetimest': request_data,
        'response': json.loads(response.data.decode('utf-8'))
    })
    log = app.logger.info("REQUEST_LOG\t%s", log_data) if response.status_code == 200 else app.logger.warning("REQUEST_LOG\t%s", log_data)
    return response