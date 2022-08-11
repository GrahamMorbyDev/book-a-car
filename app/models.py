from app import db, login
import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column('Created', db.DATETIME, default=datetime.datetime.now)
    first_name = db.Column('First name', db.String(64))
    last_name = db.Column('Last name', db.String(64))
    email = db.Column('Email', db.String(128))
    email_onbehalf = db.Column('Email On Behalf', db.String(128))
    booking_date = db.Column('Booking Date', db.DATETIME, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    bookings = db.relationship('Booking', backref='employee', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
