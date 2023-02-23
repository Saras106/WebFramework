import uuid

from flask import session, jsonify
from flask_apispec import marshal_with, doc, use_kwargs
from flask_apispec.views import MethodResource
from marshmallow import Schema, fields
from flask_restful import Resource

from app import *

x = max([int(i.user_id) for i in User.query.all()]) + 1


class SignUpRequest(Schema):
    name = fields.Str(dump_default="default name")
    username = fields.Str(dump_default="username")
    password = fields.Str(dump_default="password")
    level = fields.Int(default=0)


class LogInRequest(Schema):
    username = fields.Str(dump_default="username")
    password = fields.Str(dump_default="password")


class APIResponse(Schema):
    message = fields.Str(dump_default="Success")


class VendorResponse(Schema):
    vendor = fields.List(fields.Dict())


class ItemResponse(Schema):
    items = fields.List(fields.Dict())


class ItemRequest(Schema):
    item_id = fields.Int(default=1000)
    item_name = fields.Str(dump_default="item name")
    restaurant_name = fields.Str(dump_default="restaurant name")
    calories_per_gm = fields.Int(default=10)
    available_quantity = fields.Int(default=1)
    unit_price = fields.Int(default=1)


class PlaceOrderRequest(Schema):
    total_amount = fields.Int(default=1)


class ListCustOrderResponse(Schema):
    list_orders = fields.List(fields.Dict())


class ListOrdersResponse(Schema):
    list_all_orders = fields.List(fields.Dict())


#  Restful way of creating APIs through Flask Restful
class SignUpAPI(MethodResource, Resource):
    @doc(description='Sign Up API', tags=['SignUp API'])
    @use_kwargs(SignUpRequest, location='json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        global x
        try:
            user = User(
                x,
                kwargs['name'],
                kwargs['username'],
                kwargs['password'],
                kwargs['level'],
                1,
                datetime.datetime.utcnow())

            db.session.add(user)
            db.session.commit()
            x += 1
            return APIResponse().dump(dict(message='User is successfully Registered')), 200

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to register user:{str(e)}')), 400


api.add_resource(SignUpAPI, '/signup')
docs.register(SignUpAPI)


class LoginAPI(MethodResource, Resource):
    @doc(description='Login API', tags=['Login API'])
    @use_kwargs(LogInRequest, location='json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id']:
                return jsonify({'error': 'User already logged in'})
            user = User.query.filter_by(username=kwargs['username'], password=kwargs['password']).first()
            if user:
                print('logged in')
                session['user_id'] = user.user_id
                print(f'User ID:{str(session["user_id"])}')
                return APIResponse().dump(dict(message='User is successfully logged in')), 200
            else:
                return APIResponse().dump(dict(message='User Not Found')), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to login user:{str(e)}')), 400


api.add_resource(LoginAPI, '/login')
docs.register(LoginAPI)


class LogoutAPI(MethodResource, Resource):
    @doc(description='Logout API', tags=['Logout API'])
    @marshal_with(APIResponse)  # marshalling
    def post(self):
        try:
            if session['user_id']:
                session['user_id'] = None
                print('logged out')
                return APIResponse().dump(dict(message='User is successfully logged out')), 200

            else:
                print('user not found')
                return APIResponse().dump(dict(message='User is not logged in')), 401

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to logout user : {str(e)}')), 400


api.add_resource(LogoutAPI, '/logout')
docs.register(LogoutAPI)


class AddVendorAPI(MethodResource, Resource):
    @doc(description='Add Vendor API', tags=['Add Vendor API'])
    @marshal_with(APIResponse)
    def put(self, userid):
        try:
            if session['user_id']:
                if session['user_id'] != str(userid):
                    return jsonify({'error': 'Invalid User'})
                user = User.query.filter_by(user_id=userid).first()
                if user.level == 0:
                    user.level = 1
                    db.session.commit()
                    print("Added to Vendor")
                    return APIResponse().dump(dict(message="User is successfully added as a Vendor")), 200
                else:
                    print('User is not a Customer')
                    return APIResponse().dump(dict(message="User is not a Customer")), 401
            else:
                print('User not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able add to vendor:{str(e)}')), 400


api.add_resource(AddVendorAPI, '/add_vendor/<int:userid>', )
docs.register(AddVendorAPI)


class GetVendorsAPI(MethodResource, Resource):
    @doc(description='Get Vendors API', tags=['Get Vendors API'])
    @marshal_with(VendorResponse, APIResponse)
    def get(self):
        try:
            if session['user_id']:
                vendors = User.query.filter_by(level=1)
                vendor_list = list()
                for v in vendors:
                    ven_dict = dict()
                    ven_dict['Vendor ID'] = v.user_id
                    ven_dict['Vendor Name'] = v.name
                    items = Item.query.filter_by(vendor_id=v.user_id)
                    item_list = list()
                    for i in items:
                        item_dict = dict()
                        item_dict['Restaurant Name'] = i.restaurant_name
                        item_dict['Item Name'] = i.item_name
                        item_dict['Available Quantity'] = i.available_quantity
                        item_dict['Calorie/gm'] = i.calories_per_gm
                        item_dict['Price/unit'] = i.unit_price
                        item_list.append(item_dict)
                    ven_dict['Item List'] = item_list
                    vendor_list.append(ven_dict)
                print(vendor_list)
                return VendorResponse().dump(dict(vendor=vendor_list)), 200

            else:
                print('Not Logged In')
                return APIResponse().dump(dict(message='User Not Logged In')), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'GetVendors API not working:{str(e)}'))


api.add_resource(GetVendorsAPI, '/list_vendors')
docs.register(GetVendorsAPI)


class AddItemAPI(MethodResource, Resource):
    @doc(description='Add Item API', tags=['Add Item API'])
    @use_kwargs(ItemRequest, location='json')
    @marshal_with(APIResponse)
    def post(self, **kwargs):
        try:
            if session['user_id']:
                user = User.query.filter_by(user_id=session["user_id"], level=1).first()
                if user:
                    item = Item(
                        kwargs['item_id'],
                        user.user_id,
                        kwargs['item_name'],
                        kwargs['calories_per_gm'],
                        kwargs['available_quantity'],
                        kwargs['restaurant_name'],
                        kwargs['unit_price'],
                        1,
                        datetime.datetime.utcnow())
                    db.session.add(item)
                    db.session.commit()
                    return APIResponse().dump(dict(message='Item successfully added')), 200
                else:
                    print('No authority to add items')
                    return APIResponse().dump(dict(message='User does not have authority to add items')), 401
            else:
                print('Not logged in')
                return APIResponse().dump(dict(message='User is not logged in')), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Item cannot be added:{str(e)}')), 400


api.add_resource(AddItemAPI, '/add_item')
docs.register(AddItemAPI)


class ListItemsAPI(MethodResource, Resource):
    @doc(description='List Item API', tags=['List Item API'])
    @marshal_with(ItemResponse)
    def get(self):
        try:
            items = Item.query.all()
            item_list = list()
            for it in items:
                item_dict = dict()
                item_dict['Item ID'] = it.item_id
                item_dict['Restaurant Name'] = it.restaurant_name
                item_dict['Item Name'] = it.item_name
                item_dict['Available Quantity'] = it.available_quantity
                item_dict['Calorie/gm'] = it.calories_per_gm
                item_dict['Price/unit'] = it.unit_price
                item_dict['Creation Time'] = it.created_ts
                item_list.append(item_dict)
            print(item_list)
            return ItemResponse().dump(dict(items=item_list)), 200
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message='Not able to dump items')), 400


api.add_resource(ListItemsAPI, '/list_items')
docs.register(ListItemsAPI)


class CreateItemOrderAPI(MethodResource, Resource):
    @doc(description='Create Item Order API', tags=['Create Item Order API'])
    @marshal_with(APIResponse)
    def post(self, itemid, orderid):
        try:
            if session['user_id']:
                item = Item.query.filter_by(item_id=itemid).first()
                orders = Order.query.filter_by(order_id=orderid).first()
                if session['user_id'] != orders.user_id:
                    return jsonify({'error': 'Invalid Customer'})
                if item.available_quantity == 0:
                    return jsonify({'error': 'Order out of Stock'})
                if orders.total_amount > item.available_quantity:
                    return jsonify({'error': 'Order not available'})
                else:
                    order_items = OrderItems(
                        uuid.uuid4(),
                        orders.order_id,
                        item.item_id,
                        orders.total_amount, 1,
                        datetime.datetime.utcnow())
                    item.available_quantity = item.available_quantity - orders.total_amount

                    db.session.add(order_items)
                    db.session.commit()
                    return APIResponse().dump(dict(message='OrderItem successfully created')), 200
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'OrderItem not created:{str(e)}'))


api.add_resource(CreateItemOrderAPI, '/create_items_order/<int:itemid>/<int:orderid>')
docs.register(CreateItemOrderAPI)


class PlaceOrderAPI(MethodResource, Resource):
    @doc(description='Place Order API', tags=['Place Order API'])
    @use_kwargs(PlaceOrderRequest)
    @marshal_with(APIResponse)
    def post(self, orderid, **kwargs):
        try:
            if session['user_id']:
                user = User.query.filter_by(user_id=session["user_id"], level=0).first()
                if user:
                    order = Order(
                        orderid,
                        user.user_id,
                        kwargs['total_amount'],
                        1, 1, datetime.datetime.utcnow()
                    )
                    db.session.add(order)
                    db.session.commit()
                    return APIResponse().dump(dict(message='Placing Order was a success')), 200
                else:
                    print('Not a customer')
                    return APIResponse().dump(dict(message='Not a customer')), 401
            else:
                print('Not logged in')
                return APIResponse().dump(dict(message='Not logged in')), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Order cannot be place:{str(e)}'))


api.add_resource(PlaceOrderAPI, '/place_order/<int:orderid>')
docs.register(PlaceOrderAPI)


class ListOrdersByCustomerAPI(MethodResource, Resource):
    @doc(description='Customer Order API', tags=['Customer Order API'])
    @marshal_with(ListCustOrderResponse, APIResponse)
    def get(self, cust_id):
        try:
            if session['user_id']:
                if session['user_id'] != str(cust_id):
                    return jsonify({'error': 'Invalid User'})
                user = User.query.filter_by(user_id=cust_id).first()
                if user.level == 0:
                    order_query = Order.query.filter_by(user_id=user.user_id)
                    ord_list = list()
                    for od in order_query:
                        ord_dict = dict()
                        ord_dict['Order ID'] = od.order_id
                        order_items = OrderItems.query.filter_by(order_id=od.order_id).first()
                        ord_dict['Item ID'] = order_items.item_id
                        ord_dict['Order Quantity'] = order_items.quantity
                        ord_list.append(ord_dict)
                    print(ord_list)
                    return ListCustOrderResponse().dump(dict(list_orders=ord_list)), 200
                else:
                    print('User is not a Customer')
                    return APIResponse().dump(dict(message='User is not a customer')), 401
            else:
                print('Not Logged In')
                return APIResponse().dump(dict(message='User Not Logged In')), 401
        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Customer API API not working:{str(e)}'))


api.add_resource(ListOrdersByCustomerAPI, '/list_orders/<int:cust_id>')
docs.register(ListOrdersByCustomerAPI)


class ListAllOrdersAPI(MethodResource, Resource):
    @doc(description='List Orders API', tags=['List Orders API'])
    @marshal_with(ListOrdersResponse, APIResponse)
    def get(self):
        try:
            if session['user_id']:
                user = User.query.filter_by(user_id=session["user_id"], level=2).first()
                # k = user.level
                if user:
                    print('Admin')
                    order = Order.query.all()
                    ord_list = list()
                    for i in order:
                        ord_dict = dict()
                        ord_dict['Order ID'] = i.order_id
                        ord_dict['Customer ID'] = i.user_id
                        ord_dict['Total Amount'] = i.total_amount
                        ord_dict['Is Order Placed'] = i.is_placed
                        ord_dict['IS Active'] = i.is_active
                        ord_dict['Order Creation Time'] = i.created_ts
                        ord_list.append(ord_dict)
                    print(ord_list)
                    return ListOrdersResponse().dump(dict(list_all_orders=ord_list)), 200
                else:
                    print('Not enough Authority')
                    return APIResponse().dump(dict(message='No authority'))
            else:
                print('Admin not logged in')
                return APIResponse().dump(dict(message='Not logged in')), 401

        except Exception as e:
            print(str(e))
            return APIResponse().dump(dict(message=f'Not able to dump items:{str(e)}')), 400


api.add_resource(ListAllOrdersAPI, '/list_all_orders')
docs.register(ListAllOrdersAPI)
