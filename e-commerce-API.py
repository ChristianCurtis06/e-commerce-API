# Library integration and 'e_commerce_db' database connection
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:******@127.0.0.1/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Defining schema for 'Customers', 'Products', 'Customer_Accounts', and 'Orders' tables
class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True, validate=validate.Email)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "id")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("name", "price", "id")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

def validate_unique_username(username):
    if CustomerAccount.query.filter_by(username=username).first():
        raise ValidationError("Username already exists.")

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True, validate=validate_unique_username)
    password = fields.String(required=True, validate=validate.Length(min=6))
    customer_id = fields.Integer(required=True)

    class Meta:
        fields = ("username", "password", "customer_id", "id")

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

class OrderPostSchema(ma.Schema):
    date = fields.Date(required=True)
    delivery_date = fields.Date(required=True)
    status = fields.String(required=True)
    customer_id = fields.Integer(required=True)
    products = fields.List(fields.Integer, required=True)

    class Meta:
        fields = ("date", "delivery_date", "status", "customer_id", "products", "id")

class OrderGetSchema(ma.Schema):
    date = fields.Date()
    delivery_date = fields.Date()
    status = fields.String()
    customer_id = fields.Integer()
    products = fields.List(fields.Nested(ProductSchema))

    class Meta:
        fields = ("date", "delivery_date", "status", "customer_id", "products", "id")

order_post_schema = OrderPostSchema()
order_get_schema = OrderGetSchema()

# Defining models for 'Customers', 'Products', 'Customer_Accounts', and 'Orders' tables with the respective relationships
class Customer(db.Model):
    __tablename__ = 'Customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer')

class CustomerAccount(db.Model):
    __tablename__ = 'Customer_Accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    customer = db.relationship('Customer', backref='customer_account', uselist=False)

order_product = db.Table('Order_product',
        db.Column('order_id', db.Integer, db.ForeignKey('Orders.id'), primary_key=True),
        db.Column('product_id', db.Integer, db.ForeignKey('Products.id'), primary_key=True)
)

class Order(db.Model):
    __tablename__ = 'Orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.id'))
    products = db.relationship('Product', secondary=order_product, backref=db.backref('orders'))

class Product(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

# Setting up CRUD endpoints for 'Customers' Table
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.filter(Customer.id == id).first()
    if customer:
        result = {
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone
        }
        return jsonify(result)
    else:
        return jsonify({"error": "Customer not found in database"}), 404

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "New customer added successfully"}), 201

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.filter(Customer.id == id).first()
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    if customer:
        customer.name = customer_data['name']
        customer.email = customer_data['email']
        customer.phone = customer_data['phone']
        db.session.commit()
        return jsonify({"message": "Customer details updated successfully"}), 200
    return jsonify({"error": "Customer not found in database"}), 404

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customer = Customer.query.filter(Customer.id == id).first()

    if customer:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({"message": "Customer removed successfully"}), 200
    return jsonify({"error": "Customer not found in database"}), 404

# Setting up CRUD endpoints for 'Customer_Accounts' Table
@app.route('/customer-accounts/<int:id>', methods=['GET'])
def get_customer_account(id):
    customer_account = CustomerAccount.query.filter(CustomerAccount.id == id).first()
    if customer_account:
        result = {
            "username": customer_account.username,
            "password": customer_account.password,
            "customer_id": customer_account.customer_id,
            "name": customer_account.customer.name,
            "email": customer_account.customer.email,
            "phone": customer_account.customer.phone
        }
        return jsonify(result)
    else:
        return jsonify({"error": "Customer account not found in database"}), 404

@app.route('/customer-accounts', methods=['POST'])
def add_customer_account():
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_customer_account = CustomerAccount(username=customer_account_data['username'], password=customer_account_data['password'], customer_id=customer_account_data['customer_id'])
    db.session.add(new_customer_account)
    db.session.commit()
    return jsonify({"message": "New customer account added successfully"}), 201

@app.route('/customer-accounts/<int:id>', methods=['PUT'])
def update_customer_account(id):
    customer_account = CustomerAccount.query.filter(CustomerAccount.id == id).first()
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    if customer_account:
        customer_account.username = customer_account_data['username']
        customer_account.password = customer_account_data['password']
        customer_account.customer_id = customer_account_data['customer_id']
        db.session.commit()
        return jsonify({"message": "Customer account details updated successfully"}), 200
    return jsonify({"error": "Customer account not found in database"}), 404

@app.route('/customer-accounts/<int:id>', methods=['DELETE'])
def delete_customer_account(id):
    customer_account = CustomerAccount.query.filter(CustomerAccount.id == id).first()

    if customer_account:
        db.session.delete(customer_account)
        db.session.commit()
        return jsonify({"message": "Customer account removed successfully"}), 200
    return jsonify({"error": "Customer account not found in database"}), 404

# Setting up CRUD endpoints for 'Products' Table
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.filter(Product.id == id).first()
    if product:
        result = {
            "name": product.name,
            "price": product.price
        }
        return jsonify(result)
    else:
        return jsonify({"error": "Product not found in database"}), 404

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return products_schema.jsonify(products)

@app.route('/products', methods=['POST'])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "New product added successfully"}), 201

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.filter(Product.id == id).first()
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    if product:
        product.name = product_data['name']
        product.price = product_data['price']
        db.session.commit()
        return jsonify({"message": "Product details updated successfully"}), 200
    return jsonify({"error": "Product not found in database"}), 404

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.filter(Product.id == id).first()

    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product removed successfully"}), 200
    return jsonify({"error": "Product not found in database"}), 404

# Setting up create and read endpoints for 'Orders' Table (including tracking an order's progress)
@app.route('/orders/<int:id>', methods=['GET'])
def get_order(id):
    order = Order.query.filter(Order.id == id).first()
    if order:
        return order_get_schema.jsonify(order)
    else:
        return jsonify({"error": "Order not found in database"}), 404

@app.route('/orders', methods=['POST'])
def add_order():
    try:
        order_data = order_post_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_order = Order(date=order_data['date'], delivery_date=order_data['delivery_date'], status=order_data['status'], customer_id=order_data['customer_id'])
    
    product_ids = order_data.get('products', [])
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    if len(products) != len(product_ids):
        return jsonify({"error": "One or more product IDs are invalid"}), 400
    
    new_order.products.extend(products)

    db.session.add(new_order)
    db.session.commit()
    return jsonify({"message": "New order placed successfully"}), 201

@app.route('/orders/track-order/<int:id>', methods=['GET'])
def track_order(id):
    order = Order.query.filter(Order.id == id).first()
    if order:
        result = {
            "date": order.date,
            "delivery_date": order.delivery_date,
            "status": order.status
        }
        return jsonify(result)
    else:
        return jsonify({"message": "Order not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)