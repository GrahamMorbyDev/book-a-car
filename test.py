from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
# from flaskext.mysql import MySQL
from flask_login import LoginManager
import json

application = Flask(__name__)
application.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


# application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:omegaalpha83@localhost/carbookingapp'

db = SQLAlchemy(application)

# mysql = MySQL()
# application.config['MYSQL_DATABASE_USER'] = 'root'
# application.config['MYSQL_DATABASE_PASSWORD'] = 'omegaalpha83'
# application.config['MYSQL_DATABASE_DB'] = 'carbookingapp'
# application.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(application)

login = LoginManager(application)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
    # def __init__(self, username, password):
    #     self.username = username
    #     self.password = password

@application.route("/")
def hello():
    return "Welcome to Python Flask App!"

@application.route("/Authenticate")
def Authenticate():
    me = User(username='old', password='oldold')
    db.session.add(me)
    db.session.commit()
    username = request.args.get('UserName')
    password = request.args.get('Password')
    user = User.query.filter_by(username='old').first()
    print("Testing Query")
    print(db.engine.table_names())
    print(user.id)
    print(user.username)
    # cursor = mysql.connect().cursor()
    # cursor.execute("SELECT * from User where Username='" + username + "' and Password='" + password + "'")
    # data = cursor.fetchone()
    # if data is None:
    #  return "Username or Password is wrong"
    # else:
    return "Logged in successfully"

if __name__ == '__main__':
    db.create_all()

    # mysql.create_all()
    # app.run(debug=True, port=8000, host='127.0.0.1')
    application.run()