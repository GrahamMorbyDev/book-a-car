from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import json

application = Flask(__name__)
application.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
db = SQLAlchemy(application)
login = LoginManager(application)

from app import routes, models
