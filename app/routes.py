from app import app, db
from flask import render_template
from flask import url_for 
from flask import flash 
from flask import redirect
from flask import request, abort
from flask import jsonify
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_, and_
from flask_sqlalchemy import Pagination
from app.forms import (UserRegistrationForm, UserLoginForm, UserUpdateAccountForm)



@app.route('/')
def landing():
    return render_template('index.html')

@app.route('/user')
def user():
    #if current_user.is_authenticated: #havent check if user is user or cashier
    #    return redirect(url_for('userhome'))
    userregister_form = UserRegistrationForm()
    userlogin_form=UserLoginForm()
    if userregister_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(userregister_form.password.data).decode('utf-8')
        user = user(userid=userregister_form.username.data, name=userregister_form.name.data, email=userregister_form.email.data, password=hashed_password, contactno=userregister_form.contactno.data)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", 'success') 
        return redirect(url_for('user'))
    if userlogin_form.validate_on_submit():
        user = user.query.filter_by(username=userlogin_form.username.data).first()
        if user and bcrypt.check_password_hash(userlogin_form.password, userlogin_form.password.data):
            login_user(user, remember=userlogin_form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for('userhome'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('user.html',registerform=userregister_form, loginform=userlogin_form)

@app.route('/cashier')
def cashier():
    return render_template('cashier.html')

@app.route('/user/home',methods=['GET', 'POST'])
def userhome():
    return render_template('userlanding.html')

@app.route('/user/voucherwallet')
def uservoucherwallet():
    return render_template('notyet.html')

@app.route('/user/userQR')
def userQR():
    return render_template('notyet.html')

@app.route('/cashier/home',methods=['GET', 'POST'])
def cashierhome():
    return render_template('cashierlanding.html')

@app.route('/cashier/scanQR')
def cashierqr():
    return render_template('notyet.html')
