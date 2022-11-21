from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import msal
import json
import os
import app.app_config as app_config

basedir = os.path.abspath(os.path.dirname(__file__))

application = Flask(__name__)
application.config.from_object(app_config)
Session(application)
application.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

from werkzeug.middleware.proxy_fix import ProxyFix

application.wsgi_app = ProxyFix(application.wsgi_app, x_proto=1, x_host=1)

if "RDS_DB_NAME" in os.environ:
    application.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "mysql://{username}:{password}@{host}:{port}/{database}".format(
        username=os.environ["RDS_USERNAME"],
        password=os.environ["RDS_PASSWORD"],
        host=os.environ["RDS_HOSTNAME"],
        port=os.environ["RDS_PORT"],
        database=os.environ["RDS_DB_NAME"],
    )
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
else:
    application.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "mysql://root:omegaalpha83@localhost:3306/carbookingapp"
    # application.config[
    #     "SQLALCHEMY_DATABASE_URI"
    # ] = 'sqlite:///' + os.path.join(basedir, 'parking.db')


db = SQLAlchemy(application)


from app import routes, models
