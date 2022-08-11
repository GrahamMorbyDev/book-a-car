from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flaskext.mysql import MySQL
from flask_login import LoginManager
import json

application = Flask(__name__)
application.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:omegaalpha83@localhost/carbookingapp'
db = SQLAlchemy(application)

login = LoginManager(application)

from app import routes, models
