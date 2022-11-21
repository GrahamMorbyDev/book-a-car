from app import db, application
from app.models import Booking, User
from app.forms import LoginForm, RegistrationForm
from flask import (
    render_template,
    url_for,
    request,
    redirect,
    flash,
    jsonify,
    make_response,
    session,
)
from flask_session import Session
import msal
import requests

# from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from datetime import date, timedelta
from datetime import datetime
import json
import app.app_config as app_config

settings_file = open("parameters.json")
settings = json.load(settings_file)
DOMAINS_ALLOWED = ["leighton.com", "leighton.co.uk", "footy.com"]

print("Database Tables")
print(db.engine.table_names())


def pasttime(new_date):
    today = date.today()
    datediff = today - new_date.date()
    return datediff.days


@application.route("/")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    print(session)
    return render_template(
        "login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__
    )


@application.route(
    app_config.REDIRECT_PATH
)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args
        )
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))


# @application.route("/", methods=["GET", "POST"])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for("index"))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             flash("Invalid username or password", "alert-danger")
#             return redirect(url_for("login"))
#         login_user(user, remember=form.remember_me.data)
#         next_page = request.args.get("next")
#         if not next_page or url_parse(next_page).netloc != "":
#             next_page = url_for("index")
#         return redirect(next_page)
#     return render_template("login.html", title="Sign In", form=form)


@application.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY
        + "/oauth2/v2.0/logout"
        + "?post_logout_redirect_uri="
        + url_for("index", _external=True)
    )


@application.route("/index", methods=["GET", "POST"])
def index():
    if not session.get("user"):
        print(session)
        return redirect(url_for("login"))
    admin = 'false'

    if 'roles' in session["user"]:
        # print("roles present")
        if 'Edit' in session["user"]["roles"]:
            admin = 'true'

    #print(session["user"]["preferred_username"])
    token = _get_token_from_cache(app_config.SCOPE)
    # print(token)
    # graph_data = requests.get(  # Use token to call downstream service
    #     app_config.ENDPOINT,
    #     headers={"Authorization": "Bearer " + token["access_token"]},
    # ).json()
    # # print(graph_data)
    spaces = settings["spaces"]
    today = date.today()
    midnight = datetime.combine(today, datetime.min.time())
    bookings = Booking.query.filter(Booking.booking_date == midnight).all()
    mybookings = Booking.query.filter(
        Booking.email == session["user"]["preferred_username"]
    ).all()
    allbookings = Booking.query.all()
    count_bookings = Booking.query.filter(Booking.booking_date == midnight).count()
    old_bookings = Booking.query.filter(Booking.booking_date < midnight).all()
    currentbookings = Booking.query.filter(Booking.booking_date == midnight).all()

    for booking in old_bookings:
        # print(booking.id, booking.booking_date, booking.email)
        Booking.query.filter_by(id=booking.id).delete()
        db.session.commit()
    if request.form:
        # print(request.form)
        if "first_name" in request.form:
            if (
                (request.form["first_name"] == "")
                or (request.form["last_name"] == "")
                or (request.form["email"] != session["user"]["preferred_username"])
                or (request.form["booking_date"] == "")
                or (request.form["email_onbehalf"] == "")
            ):
                print(session["user"]["preferred_username"])
                print(request.form["email_onbehalf"])
                flash(
                    "First Name, Last Name, Email and Date must be provided!",
                    "alert-danger",
                )
            else:
                new_date = datetime.strptime(request.form["booking_date"], "%Y-%m-%d")
                count_new_bookings = Booking.query.filter(
                    Booking.booking_date == new_date
                ).count()
                datediff = pasttime(new_date)
                if datediff >= 1:
                    flash(
                        "You booking date is in the past - we can not complete the booking",
                        "alert-danger",
                    )
                elif count_new_bookings >= spaces:
                    flash(
                        "We could not complete your booking, all places are full",
                        "alert-danger",
                    )
                else:
                    new_booking = Booking(
                        first_name=request.form["first_name"],
                        last_name=request.form["last_name"],
                        email=request.form["email"],
                        email_onbehalf=request.form["email_onbehalf"],
                        booking_date=datetime.strptime(
                            request.form["booking_date"], "%Y-%m-%d"
                        ),
                    )
                    db.session.add(new_booking)
                    db.session.commit()

                    flash("Your booking was successful", "alert-success")
                    return redirect(url_for("index"))
            if count_bookings >= spaces:
                flash("All spaces are booked for today!", "alert-danger")
        if "future_date" in request.form:
            if request.form["future_date"] == "":
                flash("Date must be provided!", "alert-danger")
            else:
                future_date = datetime.strptime(request.form["future_date"], "%Y-%m-%d")
                currentbookings = Booking.query.filter(
                    Booking.booking_date == future_date
                ).all()
                print(type(currentbookings))
                future_bookings = [item.obj_to_dict() for item in currentbookings]
                # future_bookings = json.dumps([dict(r) for r in currentbookings])
                # print(type(future_bookings))
                print(future_bookings)

    return render_template(
        "index.html",
        bookings=bookings,
        mybookings=mybookings,
        currentbookings=currentbookings,
        user=session["user"],
        admin=admin,
        allbookings=allbookings,
        version=msal.__version__,
    )


@application.route("/delete", methods=["GET", "POST"])
def delete():
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        if request.form.getlist("mycheckbox"):
            for getid in request.form.getlist("mycheckbox"):
                # print(getid)
                Booking.query.filter_by(id=getid).delete()
                db.session.commit()
                # cur.execute('DELETE FROM contacts WHERE id = {0}'.format(getid))
                # conn.commit()
            flash("Successfully Deleted!", "alert-success")
    return redirect("/index")

@application.route("/delete2", methods=["GET", "POST"])
def delete2():
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        if request.form.getlist("mycheckbox2"):
            for getid in request.form.getlist("mycheckbox2"):
                # print(getid)
                Booking.query.filter_by(id=getid).delete()
                db.session.commit()
                # cur.execute('DELETE FROM contacts WHERE id = {0}'.format(getid))
                # conn.commit()
            flash("Successfully Deleted!", "alert-success")
    return redirect("/index")


@application.route("/futurebookings", methods=["GET", "POST"])
def futurebookings():
    today = date.today()
    midnight = datetime.combine(today, datetime.min.time())
    currentbookings = Booking.query.filter(Booking.booking_date == midnight).all()
    future_bookings = [item.obj_to_dict() for item in currentbookings]

    date_future = request.args.get("futuredate")
    future_date = datetime.strptime(date_future, "%Y-%m-%d")
    currentbookings = Booking.query.filter(Booking.booking_date == future_date).all()
    future_bookings = [item.obj_to_dict() for item in currentbookings]

    return render_template("future_bookings.html", message=future_bookings)


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID,
        authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET,
        token_cache=cache,
    )


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [], redirect_uri=url_for("authorized", _external=True)
    )


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


application.jinja_env.globals.update(
    _build_auth_code_flow=_build_auth_code_flow
)  # Used in template
