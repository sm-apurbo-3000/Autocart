from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from .forms import ShopItemsForm
from werkzeug.utils import secure_filename
from .models import Product
from . import db

admin = Blueprint('admin', __name__)

@admin.route('/add-shop-items', methods=['GET','POST'])
@login_required
def add_shop_items():
    if current_user.id == 1: #if admin is the current user e.g. for admin, customer.id is 1
        form = ShopItemsForm()
        
        if form.validate_on_submit():
            product_name = form.product_name.data
            previous_price = form.previous_price.data
            current_price = form.current_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            
            """Getting file, validating filename, saving to media directory"""
            file = form.product_picture.data
            file_name = secure_filename(file.filename) # Toyota Corolla.jpeg --> toyota_corolla.jpeg
            file_path = f'./media/{file_name}'
            file.save(file_path)
            
            """Pushing data in DB"""
            new_product = Product()
            new_product.product_name = product_name
            new_product.previous_price = previous_price
            new_product.current_price = current_price
            new_product.in_stock = in_stock
            new_product.flash_sale = flash_sale
            
            new_product.product_picture = file_path
            
            try:
                db.session.add(new_product)
                db.session.commit()
                flash(f'{product_name} Added for Sale Successfully!')
                return render_template('add-shop-items.html', form=form)
            
            except Exception as e:
                print(e)
                flash(f'{product_name} Failed to Add for Sale!')
            
        else:
            pass
        return render_template('add-shop-items.html', form=form)
    
    return render_template('404.html')