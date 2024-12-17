from flask import Blueprint, render_template, flash, redirect, request
from .models import Product, Cart, Wishlist
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

@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    target = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    wished_item_exists = Wishlist.query.filter_by(product_id=item_id, customer_id=current_user.id).all()

    if item_exists:
        try:
            item_exists.quantity += 1
            target.in_stock -= 1
            if target.in_stock < 1:
                target.flash_sale = False
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
        target.in_stock -= 1
        if target.in_stock < 1:
            target.flash_sale = False
        
        if wished_item_exists: # deleting from wishlist
            try:
                for item in wished_item_exists:
                    db.session.delete(item)
                db.session.commit()
            except Exception as e:
                print(e)
        
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

@views.route('/add-to-wishlist/<int:item_id>')
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