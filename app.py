from models import db, app, Booking
from flask import (render_template, url_for, request, redirect, flash)
from datetime import date
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
def index():
    spaces = 4
    today = date.today()
    midnight = datetime.combine(today, datetime.min.time())
    bookings = Booking.query.filter(Booking.booking_date == midnight).all()
    count_bookings = Booking.query.filter(Booking.booking_date == midnight).count()

    if request.form:
        new_date = datetime.strptime(request.form['booking_date'], '%Y-%m-%d')
        count_new_bookings = Booking.query.filter(Booking.booking_date == new_date).count()
        if count_new_bookings >= spaces:
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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=8000, host='127.0.0.1')
