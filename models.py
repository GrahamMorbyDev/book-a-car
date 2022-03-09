from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
db = SQLAlchemy(app)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column('Created', db.DATETIME, default=datetime.datetime.now)
    first_name = db.Column('First name', db.String)
    last_name = db.Column('Last name', db.String)
    email = db.Column('Email', db.String)
    booking_date = db.Column('Booking Date', db.DATETIME, nullable=True)

