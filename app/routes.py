from app import db, app
from app.models import Booking, User
from app.forms import LoginForm, RegistrationForm
from flask import render_template, url_for, request, redirect, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from datetime import date, timedelta
from datetime import datetime
import json

settings_file = open('parameters.json')
settings = json.load(settings_file)
DOMAINS_ALLOWED = ['leighton.com']

def pasttime(new_date):
    today = date.today()
    datediff = today - new_date.date()
    return(datediff.days)

@app.route('/helloworld', methods=['GET'])
def helloworld():
    return 'Hello World'

@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'alert-danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        email_domain = email.split('@')[-1]
        if email_domain in DOMAINS_ALLOWED:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!', 'alert-success')
            return redirect(url_for('login'))
        else:
            flash('Your email address is not valid', 'alert-danger')
    return render_template('register.html', title='Register', form=form)


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    #print(current_user.email)
    spaces = settings["spaces"]
    today = date.today()
    midnight = datetime.combine(today, datetime.min.time())
    bookings = Booking.query.filter(Booking.booking_date == midnight).all()
    mybookings = Booking.query.filter(Booking.email == current_user.email).all()
    count_bookings = Booking.query.filter(Booking.booking_date == midnight).count()
    old_bookings = Booking.query.filter(Booking.booking_date < midnight).all()

    for booking in old_bookings:
        print(booking.id, booking.booking_date, booking.email)
        Booking.query.filter_by(id=booking.id).delete()
        db.session.commit()
    if request.form:
        if (request.form['first_name'] == '') or (request.form['last_name'] == '') or \
            (request.form['email'] != current_user.email) or (request.form['booking_date'] == '') or \
            (request.form['email_onbehalf'] == ''):
                print(current_user.email)
                print(request.form['email_onbehalf'])
                flash('First Name, Last Name, Email and Date must be provided!', 'alert-danger')
        else:
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
                    email_onbehalf=request.form['email_onbehalf'],
                    booking_date=datetime.strptime(request.form['booking_date'], '%Y-%m-%d')
                )
                db.session.add(new_booking)
                db.session.commit()
                flash('Your booking was successful', 'alert-success')
                return redirect(url_for('index'))
        if count_bookings >= spaces:
            flash('All spaces are booked for today!', 'alert-danger')
    return render_template('index.html', bookings=bookings, mybookings=mybookings)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    #cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        if request.form.getlist('mycheckbox'):
            for getid in request.form.getlist('mycheckbox'):
                #print(getid)
                Booking.query.filter_by(id=getid).delete()
                db.session.commit()
                #cur.execute('DELETE FROM contacts WHERE id = {0}'.format(getid))
                #conn.commit()
            flash('Successfully Deleted!', 'alert-success')
    return redirect('/index')
