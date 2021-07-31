from flask_login.mixins import UserMixin
from app import app, db, bcrypt, login_manager
from flask import render_template
from flask import url_for 
from flask import flash 
from flask import redirect
from flask import request, abort
from flask import jsonify
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_, and_
from flask_sqlalchemy import Pagination
<<<<<<< HEAD
from app.forms import (UserRegistrationForm, UserLoginForm, UpdateAccountForm, CashierRegistrationForm,CashierLoginForm)
from app.models import (User,Voucher,Vouchercat)
=======
from app.forms import (UserRegistrationForm, UserLoginForm, UserUpdateAccountForm, CashierRegistrationForm,CashierLoginForm)
from app.models import (User, Voucher, Vouchercat)
>>>>>>> 27e94dd5fea8c420cc5eebd8de4cc84ccc39503d

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')

@app.route('/',methods=['GET', 'POST'])
def landing():
    return render_template('index.html')

@app.route('/user',methods=['GET', 'POST'])
def users():
    if current_user.is_authenticated: 
        return redirect(url_for('userhome'))
    userregister_form = UserRegistrationForm()
    userlogin_form=UserLoginForm()
    if userregister_form.validate_on_submit():
        print('valid')
        hashed_password = bcrypt.generate_password_hash(userregister_form.password.data).decode('utf-8')
        user = User(username=userregister_form.username.data, password=hashed_password,email=userregister_form.email.data,cashier=0)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", 'success') 
        return redirect('/user#login')
    if userlogin_form.validate_on_submit():
        user = User.query.filter_by(username=userlogin_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, userlogin_form.password.data) and user.cashier==0:
            login_user(user, remember=userlogin_form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for('userhome'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('user.html',userregister_form=userregister_form, userlogin_form=userlogin_form)

@app.route('/cashier',methods=['GET', 'POST'])
def cashier():
    if current_user.is_authenticated: 
        return redirect(url_for('userhome'))
    cashierregister_form = CashierRegistrationForm()
    cashierlogin_form=CashierLoginForm()
    if cashierregister_form.validate_on_submit():
        print('valid')
        hashed_password = bcrypt.generate_password_hash(cashierregister_form.password.data).decode('utf-8')
        user = User(username=cashierregister_form.username.data, password=hashed_password,email=cashierregister_form.email.data,cashier=1)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", 'success') 
        return redirect('/cashier#login')
    if cashierlogin_form.validate_on_submit():
        user = User.query.filter_by(username=cashierlogin_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, cashierlogin_form.password.data) and user.cashier==1:
            login_user(user, remember=cashierlogin_form.remember.data)
            next_page = request.args.get('next')
            return redirect(url_for('cashierhome'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('cashier.html',cashierregister_form=cashierregister_form, cashierlogin_form=cashierlogin_form)

@app.route('/user/home',methods=['GET', 'POST'])
@login_required 
def userhome():
    data = Vouchercat.query.filter(Vouchercat.quantity>0).all()
    return render_template('userlanding.html', data=data)

@app.route('/user/voucherwallet')
@login_required
def uservoucherwallet():
    return render_template('notyet.html')

@app.route('/voucher/<int:userid>')
@login_required
def voucher(userid):
    return render_template('notyet.html', userid=userid)

@app.route('/user/userQR')
@login_required
def userQR():
    return render_template('notyet.html')

@app.route('/cashier/home',methods=['GET', 'POST'])
@login_required
def cashierhome():
    return render_template('cashierlanding.html')

@app.route("/cashier/account", methods=['GET', 'POST'])
@login_required 
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.photo.data:
            picture_file = save_picture(form.picture.data)
            current_user.photo = picture_file
        current_user.address = form.address.data
        current_user.contactno = form.contactno.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        flash('Your account info has been updated', 'success')
        return redirect(url_for('account'))
    #elif request.method == 'GET':
    image_file = url_for('static', filename='uploads/' + current_user.photo) 
    return render_template('cashierprofile.html', title="Profile", image_file=image_file, form=form)


@app.route('/cashier/scanQR')
@login_required
def cashierqr():
    return render_template('scanqr.html')

@app.route("/user/logout")
@login_required
def logoutuser():
    logout_user()
    return redirect(url_for('users'))

@app.route("/cashier/logout")
@login_required
def logoutcashier():
    logout_user()
    return redirect(url_for('cashier'))