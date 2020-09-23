from flask import (
                    Flask, request, jsonify,
                    make_response,url_for,
                    redirect, render_template, session
                  )
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask.views import View
from flask.views import MethodView
import time
import os
import sqlite3
import jwt
import datetime
from functools import wraps
# init app..
app = Flask(__name__)
# init api..
api = Api(app)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] ='thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir,'db1.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# init db.
db = SQLAlchemy(app)
# init marshmallow
ma = Marshmallow(app)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    salary = db.Column(db.Float)
    active = db.Column(db.Boolean)

    def __init__(self, name, salary, active):
        self.name = name
        self.salary = salary
        self.active = active

    def __str__(self):
        return f"Employee: {self.name}"

class EmployeeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'salary', 'active')

employee_schema = EmployeeSchema()
employees_schema = EmployeeSchema(many=True)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        #new_token = request.args.get('token')
        token = request.cookies.get('my_token')
        print(token)
        if not token:
            return jsonify({'Message':'Token is Missing, You Must login @ /login url..'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            print(data)
        except:
            return jsonify({'Message':'Token is invalid, Login again to generate a new token.'})
        return f(*args, **kwargs)
    return decorated

@app.route('/login/', methods=['GET'])
def login():
    auth = request.authorization
    if auth and auth.password == "password":
        token = jwt.encode({'user':auth.username,'exp':datetime.datetime.utcnow() + datetime.timedelta(seconds=20)},app.config['SECRET_KEY'])
        token = token.decode('UTF-8')
        print(token)
        response = make_response(redirect(url_for('listcreateemployee')))
        response.set_cookie('my_token',token)
        #session['token'] = token
        #app.permanent_session_lifetime = datetime.timedelta(seconds=10)
        return response
    return make_response("We couldn't verify you, try again by providing proper credentials! :)",401, {'WWW-Authenticate':'Basic realm="Login Required"'})

@app.route('/mycookie/')
def getcookie():
    token = request.cookies.get('my_token')
    if token:
        return "Getting cokkies data: " + token
    else:
        return "There is No cookie.."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_background/<mode>')
def set_background(mode):
    session['mode'] = mode
    #session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(seconds=60)
    print(session)
    return redirect(url_for('index'))

@app.route('/drop_session')
def drop_session():
    session.pop('mode',None)
    return redirect(url_for('index'))

# USING RESOURCE CLASSES FOR EXPOSING DATA..
class ListCreateEmployee(Resource, MethodView):
    decorators = [token_required]
    def get(self):
        employees = Employee.query.all()
        return employees_schema.jsonify(employees)

    def post(self):
        name = request.json['name']
        salary = request.json['salary']
        active = request.json['active']
        create_employee = Employee(name, salary, active)
        db.session.add(create_employee)
        db.session.commit()
        return employee_schema.jsonify(create_employee)

class RetrieveUpdateDeleteEmployee(Resource, MethodView):
    decorators = [token_required]
    def get(self, id):
        employee = Employee.query.get(id)
        return employee_schema.jsonify(employee)
    def put(self, id):
        employee = Employee.query.get(id)
        name = request.json['name']
        salary = request.json['salary']
        active = request.json['active']
        employee.name = name
        employee.salary = salary
        employee.active = active
        db.session.commit()
        return employee_schema.jsonify(employee)

    def delete(self, id):
        employee = Employee.query.get(id)
        db.session.delete(employee)
        db.session.commit()
        return employee_schema.jsonify(employee)

api.add_resource(ListCreateEmployee, '/employees/')
api.add_resource(RetrieveUpdateDeleteEmployee, '/employees/<id>/')
# run server
if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000,debug=True,use_reloader=True)
