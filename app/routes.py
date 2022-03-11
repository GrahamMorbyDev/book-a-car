from app import db, app
from app.models import Booking
from flask import (render_template, url_for, request, redirect, flash)
from datetime import date, timedelta
from datetime import datetime
import json

settings_file = open('parameters.json')
settings = json.load(settings_file)

def pasttime(new_date):
    today = date.today()
    datediff = today - new_date.date()
    return(datediff.days)

@app.route('/helloworld', methods=['GET'])
def helloworld():
    return 'Hello World'

@app.route('/', methods=['GET', 'POST'])
def index():
    spaces = settings["spaces"]
    today = date.today()
    midnight = datetime.combine(today, datetime.min.time())
    bookings = Booking.query.filter(Booking.booking_date == midnight).all()
    count_bookings = Booking.query.filter(Booking.booking_date == midnight).count()

    if request.form:
        new_date = datetime.strptime(request.form['booking_date'], '%Y-%m-%d')
        count_new_bookings = Booking.query.filter(Booking.booking_date == new_date).count()
        datediff = pasttime(new_date)
        if datediff >= 1:
            flash('You booking date is in the past - we can not complete the booking')
        elif count_new_bookings >= spaces:
            flash('We could not complete your booking, all places are full')
        else:
            new_booking = Booking(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                email=request.form['email'],
                booking_date=datetime.strptime(request.form['booking_date'], '%Y-%m-%d')
            )
            db.session.add(new_booking)
            db.session.commit()
            flash('Your booking was successful')
            return redirect(url_for('index'))
    if count_bookings >= spaces:
        flash('All spaces are booked for today!')
    return render_template('index.html', bookings=bookings)

