from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Wishlist, Order
from flask_login import login_required, current_user
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    products = Product.query.filter_by(flash_sale=True)
    
    # for dsplaying count on the cart icon
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(customer_link=current_user.id).all()
        wished_items = Wishlist.query.filter_by(customer_id=current_user.id).all()
    else:
        cart_items = []
        wished_items = []

    return render_template('home.html', items=products, cart_items=cart_items, wished_items=wished_items)

@views.route('/add-to-cart/<int:item_id>', methods = ['GET','POST'])
@login_required
def add_to_cart(item_id):
    target = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    

    if item_exists:
        try:
            item_exists.quantity += 1
            db.session.commit()
            flash(f'Quantity updated for {item_exists.product.product_name}!')
            return redirect(request.referrer) # after adding to cart, return to referrer page e.g. home page.
        
        except Exception as e:
            print(e)
            flash(f'Quantity update failed for {item_exists.product.product_name}!')
            return redirect(request.referrer) # return to referrer page e.g. home page.
    
    new_cart_item = Cart()
    new_cart_item.quantity = 1 # default quantity is 1
    new_cart_item.product_link = target.id # id of added product
    new_cart_item.customer_link = current_user.id # id of customer

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} added to cart successfully!')
    
    except Exception as e:
        print(e)
        flash(f'{new_cart_item.product.product_name} failed to add to cart!')
    
    return redirect(request.referrer) # return to home page.


@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    
    for item in cart:
        amount += (item.product.current_price * item.quantity)
    
    return render_template('cart.html', cart=cart, amount=amount, total=(amount+10000))

@views.route('/add-to-wishlist/<int:item_id>', methods = ['GET','POST'])
@login_required
def add_to_wishlist(item_id):
    target = Product.query.get(item_id)
    wished_item_exists = Wishlist.query.filter_by(customer_id=current_user.id, product_id=item_id).all()

    if wished_item_exists:
        flash(f'{target.product_name} already exists in your wishlist.')
    
    else:
        wished_item = Wishlist(customer_id=current_user.id, product_id=target.id)

        try:
            db.session.add(wished_item)
            db.session.commit()
            flash(f'{wished_item.product.product_name} added to your wishlist successfully!')
        
        except Exception as e:
            print(e)
            flash(f'{wished_item.product.product_name} failed to add to your wishlist!')
        
    return redirect(request.referrer)

@views.route('/remove-from-wishlist/<int:item_id>')
@login_required
def remove_from_wishlist(item_id):
    target = Wishlist.query.filter_by(customer_id=current_user.id, product_id=item_id).all()
    try:
        for item in target:
            db.session.delete(item)
        db.session.commit()
        flash(f'Wishlist updated successfully!')
    
    except Exception as e:
        print(e)
    
    return redirect(request.referrer)

@views.route('/wishlist')
@login_required
def show_wishlist():
    # for dsplaying count on the cart icon
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(customer_link=current_user.id).all()
        wished_items = Wishlist.query.filter_by(customer_id=current_user.id).all()
    else:
        cart_items = []
        wished_items = []

    return render_template('wishlist.html', cart_items=cart_items, wished_items=wished_items)


@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        if cart_item.product.in_stock > 0:
            cart_item.quantity += 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        
        amount=0
        for item in cart:
            amount += (item.product.current_price * item.quantity)

        data = {'quantity': cart_item.quantity, 'amount': amount, 'total': amount + 10000}

        return jsonify(data)


@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        
        amount=0
        for item in cart:
            amount += (item.product.current_price * item.quantity)
            
        data = {'quantity': cart_item.quantity, 'amount': amount, 'total': amount + 10000}

        return jsonify(data)

@views.route('/remove-cart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount=0
        for item in cart:
            amount += (item.product.current_price * item.quantity)
            
        data = {'quantity': cart_item.quantity, 'amount': amount, 'total': amount + 10000}

        return jsonify(data)
    

# ============================PAYMENT GATEWAY========================== # success, failure, cancel TBD
import requests
from flask import jsonify

SSL_COMMERZ_STORE_ID = 'autoc6769be61e1afb'
SSL_COMMERZ_STORE_PASSWORD = 'autoc6769be61e1afb@ssl'

@views.route('/place-order')
@login_required
def place_order():
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
    
    if customer_cart:
        try:
            total = 0
            for item in customer_cart:
                total += item.product.current_price * item.quantity

            payment_data = {
                'store_id': SSL_COMMERZ_STORE_ID,
                'store_passwd': SSL_COMMERZ_STORE_PASSWORD,
                'total_amount': total + 10000,  # including shipping charge
                'currency': 'BDT',
                'tran_id': f'TRX_{int(total * 100)}_{current_user.id}',
                'success_url': 'http://localhost:5000/payment-success',
                'fail_url': 'http://localhost:5000/payment-failure',
                'cancel_url': 'http://localhost:5000/payment-cancel',
                'cus_name': current_user.username,
                'cus_email': current_user.email,
                'cus_phone': '01777777777',
                'cus_add1': 'Customer Address',
                'cus_city': 'Dhaka',
                'cus_country': 'Bangladesh',
                'shipping_method': 'NO',
                'num_of_item': len(customer_cart),
                'product_name': 'Cart Items',
                'product_category': 'General',
                'product_profile': 'general',
            }

            response = requests.post('https://sandbox.sslcommerz.com/gwprocess/v4/api.php', data=payment_data)
            payment_response = response.json()
            print("Parsed Payment Response:", payment_response)

            if payment_response.get('status') == 'SUCCESS':
                for item in customer_cart:
                    new_order = Order()
                    new_order.quantity = item.quantity
                    new_order.price = item.product.current_price
                    new_order.status = 'Pending'
                    new_order.payment_id = payment_response['sessionkey']

                    new_order.product_link = item.product_link
                    new_order.customer_link = item.customer_link

                    db.session.add(new_order)

                    product = Product.query.get(item.product_link)
                    product.in_stock -= item.quantity

                    if product.in_stock < 1:
                        product.flash_sale = False
                    
                    wished_item_exists = Wishlist.query.filter_by(product_id=item.product.id, customer_id=current_user.id).all()
                    
                    if wished_item_exists: # deleting from wishlist
                        try:
                            for w in wished_item_exists:
                                db.session.delete(w)
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()
                            print(e)

                    db.session.delete(item)

                db.session.commit()

                flash('Redirecting to payment gateway...')
                return redirect(payment_response['GatewayPageURL'])
            else:
                print("Payment initialization failed:", payment_response)
                flash('Payment initialization failed. Please try again.')
                return redirect('/cart')

        except Exception as e:
            db.session.rollback()
            print(f"Order not placed due to: {e}")
            return redirect('/cart')
    else:
        flash('Your cart is Empty')
        return redirect('/cart')

# ====================================================================================

@views.route('/orders')
@login_required
def show_orders():
    orders = Order.query.filter_by(customer_link = current_user.id).all()
    return render_template('orders.html', orders = orders)


@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_keyword = request.form.get('search')
        search_items = Product.query.filter(Product.product_name.ilike(f'%{search_keyword}%')).all()
        return render_template('search.html', items=search_items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])
    
    flash(f'Ops! Something went wrong.')
    return render_template('search.html')

@views.route('/product-details/<int:item_id>')
def product_details(item_id):
   target = Product.query.get(item_id)
   if target:
       data = {'product_id':item_id,
               'product_name':target.product_name,
               'product_details':target.product_details,
               'current_price':target.current_price,
               'previous_price':target.previous_price,
               'in_stock':target.in_stock,
               'product_picture':target.product_picture,
               'date_added':target.date_added
               }
       return render_template('product_details.html', data=data)
   return render_template('404.html')