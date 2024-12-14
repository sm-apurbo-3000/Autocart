from flask import Blueprint, render_template, flash, redirect
from .forms import LoginForm, SignUpForm, PasswordChangeForm
from .models import Customer
from . import db
from flask_login import login_user, login_required, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/sign-up', methods = ['GET', 'POST'])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit(): # if it is a POST req. and data validated
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data

        if password1 == password2: # @password.setter method gets called
            new_customer = Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.password = password2

            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Account Created Successfully!')
                return redirect('/login')
            
            except Exception as e:
                print(e)
                flash('Account Creation Failed! Email already exists.')
            
            form.email.data = ''
            form.username.data = ''
            form.password1.data = ''
            form.password2.data = ''

    return render_template('signup.html', form = form)

@auth.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit(): # if it is a POST req. and data validated
        email = form.email.data
        password = form.password.data

        customer = Customer.query.filter_by(email = email).first()

        if customer: # if customer exists in db
            
            if customer.verify_password(password = password): #returns Boolean
                login_user(customer)
                return redirect('/') # redirect ot homepage
            else:
                flash('Incorrect Credentials')

        else:
            flash('Account does not exist! Please Sign Up first.')

    return render_template('login.html', form = form)


@auth.route('/logout', methods = ['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    return redirect('/') # redirect ot homepage


@auth.route('/profile/<int:customer_id>') # profile/1or2or3... => dynamic url for profile to share same template
@login_required
def profile(customer_id): # for profile view function
    customer = Customer.query.get(customer_id)
    print(f'Customer ID: {customer_id}')
    return render_template('profile.html', customer = customer)

@auth.route('/change-password/<int:customer_id>', methods = ['GET', 'POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)

    if form.validate_on_submit(): # if it is a POST req. and data validated
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            
            if new_password == confirm_new_password:
                customer.password = confirm_new_password
                db.session.commit()
                flash('Password has been updated successfully!')
                return redirect(f'/profile/{customer.id}') # dynamic url
            
            else:
                flash('Passwords do not match!')

        else:
            flash('Current Password in Incorrect!')


    return render_template('change-password.html', form = form)