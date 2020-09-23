from flask import Flask,request,jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from functools import wraps
import os
import jwt
import datetime
import sqlite3

# Init app.
app = Flask(__name__)

# Base Directory.
base_dir = os.path.abspath(os.path.dirname(__file__))
print(base_dir)

#Init database..
app.config['SECRET_KEY'] = 'thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#Init Marshmallow
ma = Marshmallow(app)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'Message':'Token is Missing'})
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Message':'Token is Invalid or Expired!'})
        return f(*args, **kwargs)
    return decorated

@app.route('/protected')
def protected():
    auth = request.authorization
    if auth and auth.password=="password":
        token = jwt.encode({'user':auth.username,'exp':datetime.datetime.utcnow()+datetime.timedelta(seconds=300)},app.config['SECRET_KEY'])
        return jsonify({'token':token.decode('UTF-8')})
    return make_response("Could not verify",401,{'WWW-Authenticate':'Basic realm="Login Required"'})

# Product Model/class
class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(100))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self,name,description,price,qty):
        self.name = name
        self.description = description
        self.price = price
        self.qty = qty

#ProductSchema

class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name','description', 'price', 'qty')

#single product_schema
product_schema = ProductSchema()
#Many Products
products_schema = ProductSchema(many=True)

@app.route('/products/', methods=['GET','POST'])
@token_required
def create_list_product():
    if request.method == "POST":
        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        qty = request.json['qty']

        new_product = Product(name,description,price,qty)
        db.session.add(new_product)
        db.session.commit()
        return product_schema.jsonify(new_product)
    elif request.method == "GET":
        all_products = Product.query.all()
        # result = products_schema.dump(all_products)
        # return products_schema.jsonify(result)
        return products_schema.jsonify(all_products)

@app.route('/products/<int:id>/', methods=['GET','PUT','DELETE'])
@token_required
def all_products(id):
    if request.method == "GET":
        products = Product.query.get(id)
        return product_schema.jsonify(products)
    if request.method == "PUT":
        product = Product.query.get(id)
        name = request.json['name']
        description = request.json['description']
        price = request.json['price']
        qty = request.json['qty']
        product.name = name
        product.description = description
        product.price = price
        product.qty = qty
        db.session.commit()
        return product_schema.jsonify(product)
    if request.method == "DELETE":
        product = Product.query.get(id)
        db.session.delete(product)
        db.session.commit()
        return product_schema.jsonify(product)
#Run server
if __name__ == '__main__':
    app.run(port=5001,debug=True)
