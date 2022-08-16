from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import json
import os

application = Flask(__name__)
application.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

if 'RDS_DB_NAME' in os.environ:
    application.config['SQLALCHEMY_DATABASE_URI'] = \
        'mysql://{username}:{password}@{host}:{port}/{database}'.format(
        username=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD'],
        host=os.environ['RDS_HOSTNAME'],
        port=os.environ['RDS_PORT'],
        database=os.environ['RDS_DB_NAME'],
        )
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
else:
    application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:omegaalpha83@localhost/carbookingapp'

db = SQLAlchemy(application)

login = LoginManager(application)



from app import routes, models
