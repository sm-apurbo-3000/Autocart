from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash



class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100), unique = True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(150))
    date_joined = db.Column(db.DateTime(), default = datetime.utcnow)

    cart_items = db.relationship('Cart', backref = db.backref('customer', lazy = True)) # lazy => True: SQLAlchemy will load related data form DB
    orders = db.relationship('Order', backref = db.backref('customer', lazy = True))
    wishlist_items = db.relationship('Wishlist', backref = db.backref('customer', lazy = True))

    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password = password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password = password)
    
    def __str__(self):
        return '<Customer %r>' % Customer.id # for printing customer id from instances --> print(customer1) => <Customer 1>


class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    product_name = db.Column(db.String(100), nullable = False)
    current_price = db.Column(db.Float, nullable = False)
    previous_price = db.Column(db.Float, nullable = False)
    in_stock = db.Column(db.Integer, nullable = False)
    product_picture = db.Column(db.String(1000), nullable = False)
    flash_sale = db.Column(db.Boolean, default = False)
    date_added = db.Column(db.DateTime, default = datetime.utcnow)

    carts = db.relationship('Cart', backref = db.backref('product', lazy = True))
    orders = db.relationship('Order', backref = db.backref('product', lazy = True))
    wishlist_items = db.relationship('Wishlist', backref = db.backref('product', lazy = True))

    def __str__(self):
        return '<Product %r>' % self.product_name

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.Integer, nullable = False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable = False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)

    def __str__(self):
        return '<Cart %r>' % self.id
    
    #cart_item_one.customer.customer_attr
    #cart_item_one.product.product_attr

class Order(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.Integer, nullable = False)
    price = db.Column(db.Float, nullable = False)
    status = db.Column(db.String(100), nullable = False)
    payment_id = db.Column(db.String(1000), nullable = False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable = False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable = False)

    #order_item_one.customer.customer_attr
    #order_item_one.product.product_attr

    def __str__(self):
        return '<Order %r>' % self.id

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Assuming product_id exists in a Product model
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)

    #wishlist_item_one.customer.customer_attr
    #wishlist_item_one.product.product_attr

    def __str__(self):
        return '<Wishlist %r>' % self.id