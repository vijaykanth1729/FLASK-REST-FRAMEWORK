from flask import Flask, jsonify, request
from flask_restful import Resource,Api
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import os
import datetime


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'myflask.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.name}"

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@app.route('/')
def home():
    return "<h1>Welcome to Flask</h1>"

@app.route('/products/',methods=['GET','POST'])
def products_list():
    if request.method == "GET":
        products = Product.query.all()
        return products_schema.jsonify(products)
    if request.method == "POST":
        name = request.json['name']
        description = request.json['description']
        new_data = Product(name,description)
        db.session.add(new_data)
        db.session.commit()
        return product_schema.jsonify(new_data)
@app.route('/products/<id>/',methods=['GET','PUT', 'DELETE'])
def products_detail(id):
    if request.method == "GET":
        product = Product.query.get(id)
        return product_schema.jsonify(product)
    if request.method == "PUT":
        name = request.json['name']
        description = request.json['description']
        product = Product.query.get(id)
        product.name = name
        product.description = description
        db.session.commit()
        return product_schema.jsonify(product)
    if request.method == "DELETE":
        product = Product.query.get(id)
        db.session.delete(product)
        db.session.commit()
        return product_schema.jsonify(product)
    
if __name__ == '__main__':
    app.run(debug=True)
