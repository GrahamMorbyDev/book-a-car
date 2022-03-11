from app import db
import datetime


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column('Created', db.DATETIME, default=datetime.datetime.now)
    first_name = db.Column('First name', db.String)
    last_name = db.Column('Last name', db.String)
    email = db.Column('Email', db.String)
    booking_date = db.Column('Booking Date', db.DATETIME, nullable=True)

