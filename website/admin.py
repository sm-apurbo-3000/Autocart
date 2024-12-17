from flask import Blueprint, render_template, flash, send_from_directory, redirect
from flask_login import login_required, current_user
from .forms import ShopItemsForm
from werkzeug.utils import secure_filename
from .models import Product
from . import db

admin_id=[1]
admin = Blueprint('admin', __name__)

@admin.route('/add-new-car', methods=['GET','POST'])
@login_required
def add_new_car():
    if current_user.id in admin_id: # checks if admin or not by uid
        form = ShopItemsForm()
        
        if form.validate_on_submit():
            # retriving data from form
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename) # toyota corolla.jpeg => toyota_corolla.jpeg
            file_path = f'./media/{file_name}'
            file.save(file_path)

            # creating new car obj
            new_car = Product()
            new_car.product_name = product_name
            new_car.current_price = current_price
            new_car.previous_price = previous_price
            new_car.in_stock = in_stock
            new_car.flash_sale = flash_sale
            new_car.product_picture = file_path

            try:
                db.session.add(new_car)
                db.session.commit()
                flash(f'{product_name} has been added successfully and up for sale!')
                render_template('add-new-car.html', form = form)
            
            except Exception as e:
                print(e)
                flash(f'{product_name} has not been added for sale!')


        return render_template('add-new-car.html', form = form)

    return render_template('404.html')


@admin.route('/show-added-cars', methods=['GET', 'POST'])
@login_required
def show_added_cars():
    if current_user.id in admin_id: # checks if admin or not by uid
        added_cars = Product.query.order_by(Product.date_added).all()
        return render_template('show_added_cars.html', items=added_cars)
    return render_template('404.html')


@admin.route('/media/<path:filename>')
def get_image(filename): # for dsiplaying product pic
    return send_from_directory('../media', filename)


@admin.route('/update-product/<int:item_id>', methods=['GET','POST'])
@login_required
def update_car(item_id):
    if current_user.id in admin_id:
        form = ShopItemsForm()
        target_product = Product.query.get(item_id)

        # for placeholder with previous data before update
        form.product_name.render_kw = {'placeholder':target_product.product_name}
        form.previous_price.render_kw = {'placeholder':target_product.previous_price}
        form.current_price.render_kw = {'placeholder':target_product.current_price}
        form.in_stock.render_kw = {'placeholder':target_product.in_stock}
        form.flash_sale.render_kw = {'placeholder':target_product.flash_sale}

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            file = form.product_picture.data
            file_name = secure_filename(file.filename) # toyota corolla.jpeg => toyota_corolla.jpeg
            file_path = f'./media/{file_name}'
            file.save(file_path)

            try:
                Product.query.filter_by(id=item_id).update(dict(product_name=product_name,
                                                                current_price=current_price,
                                                                previous_price=previous_price,
                                                                in_stock=in_stock,
                                                                flash_sale=flash_sale,
                                                                product_picture=file_path))
                db.session.commit()
                flash(f'{product_name} has been updated successfully!')
                return redirect('/show-added-cars')
            
            except Exception as e:
                print(e)
                flash(f'Update Operation Failed!')

        return render_template('update_car.html', form=form)
    
    return render_template('404.html')

@admin.route('/remove-product/<int:item_id>', methods=['GET','POST'])
@login_required
def remove_product(item_id):
    if current_user.id in admin_id:
        try:
            target = Product.query.get(item_id)
            db.session.delete(target)
            db.session.commit()
            flash(f'{target.product_name} has been removed successfully!')
            return redirect('/show-added-cars')
        
        except Exception as e:
            print(e)
            flash(f'{target.product_name} removal failed!')

        return redirect('/show-added-cars')

    return render_template('404.html')