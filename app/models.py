from app import application
import datetime
from flask_sqlalchemy import SQLAlchemy

application.config['DEBUG'] = True
application.config['ENV'] = 'development'
application.config['FLASK_ENV'] = 'development'
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/restaurant'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
application.config['SQLALCHEMY_ECHO'] = True
application.app_context().push()
db = SQLAlchemy(application)


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(200), unique=True)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    level = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Integer, default=1)
    created_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_ts = db.Column(db.DateTime)

    def __init__(self, user_id, name, username, password, level, is_active, created_ts):
        self.user_id = user_id
        self.name = name
        self.username = username
        self.password = password
        self.level = level
        self.is_active = is_active
        self.created_ts = created_ts


class Item(db.Model):
    __tablename__ = 'item'

    item_id = db.Column(db.String(100), primary_key=True)
    vendor_id = db.Column(db.String(100), db.ForeignKey("user.user_id"))
    item_name = db.Column(db.String(500))
    calories_per_gm = db.Column(db.Integer)
    available_quantity = db.Column(db.Integer)
    restaurant_name = db.Column(db.String(500))
    unit_price = db.Column(db.Integer)
    is_active = db.Column(db.Integer, default=1)
    created_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_ts = db.Column(db.DateTime)

    def __init__(self, item_id, vendor_id, item_name, calories_per_gm, available_quantity,
                 restaurant_name, unit_price, is_active, created_ts):
        self.item_id = item_id
        self.vendor_id = vendor_id
        self.item_name = item_name
        self.calories_per_gm = calories_per_gm
        self.available_quantity = available_quantity
        self.restaurant_name = restaurant_name
        self.unit_price = unit_price
        self.is_active = is_active
        self.created_ts = created_ts


class Order(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey("user.user_id"))
    total_amount = db.Column(db.Integer, default=0)
    is_placed = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Integer, default=1)
    created_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_ts = db.Column(db.DateTime)

    def __init__(self, order_id, user_id, total_amount, is_placed, is_active, created_ts):
        self.order_id = order_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.is_placed = is_placed
        self.is_active = is_active
        self.created_ts = created_ts


class OrderItems(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.String(100), primary_key=True)
    order_id = db.Column(db.String(100), db.ForeignKey("orders.order_id"))
    item_id = db.Column(db.String(100), db.ForeignKey("item.item_id"))
    quantity = db.Column(db.Integer)
    is_active = db.Column(db.Integer, default=1)
    created_ts = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    updated_ts = db.Column(db.DateTime)

    def __init__(self, id, order_id, item_id, quantity, is_active, created_ts):
        self.id = id
        self.order_id = order_id
        self.item_id = item_id
        self.quantity = quantity
        self.is_active = is_active
        self.created_ts = created_ts


db.create_all()
db.session.commit()
