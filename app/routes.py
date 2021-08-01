from flask_login.mixins import UserMixin
from app import app, db, bcrypt, login_manager
from flask import render_template
from flask import jsonify, make_response
from flask import url_for 
from flask import flash 
from flask import redirect
from flask import request, abort
from flask import jsonify
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_, and_
from flask_sqlalchemy import Pagination
from app.forms import (UserRegistrationForm, UserLoginForm, BuyForm, UpdateAccountForm, CashierRegistrationForm,CashierLoginForm)
from app.models import (User, Voucher, Vouchercat)
import qrcode
import datetime

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
    voucher_data = Voucher.query.filter_by(username = current_user.username).all()
    distinct_cashiers = []
    for i in range(len(voucher_data)):
        if voucher_data[i].cashiername not in distinct_cashiers:
            distinct_cashiers.append(voucher_data[i].cashiername)
    if len(distinct_cashiers) == 0 :
        return render_template('emptywallet.html')
    else:
        return render_template('wallet.html', data=distinct_cashiers)

@app.route('/user/voucherwallet/<string:cashiername>',methods=['GET', 'POST'])
@login_required 
def uservoucher(cashiername):
    vouchers_owned = Voucher.query.filter_by(username = current_user.username, cashiername=cashiername, status = 1)
    return render_template('uservoucher.html', data=vouchers_owned)

@app.route('/user/voucherwallet/<string:cashiername>/unavailable',methods=['GET', 'POST'])
@login_required 
def unavailablevoucher(cashiername):
    unavailable_vouchers = Voucher.query.filter(Voucher.status != 1, Voucher.username == current_user.username, Voucher.cashiername==cashiername).all()
    if len(unavailable_vouchers) == 0 :
        return render_template('emptyvoucher.html', data=cashiername)
    else:
        return render_template('uservoucher.html', data=unavailable_vouchers)

@app.route('/user/voucherwallet/<string:cashiername>/<int:voucherid>',methods=['GET', 'POST'])
@login_required 
def voucherqr(cashiername, voucherid):
    voucher = Voucher.query.filter_by(id = voucherid)
    qr = qrcode.make('{}'.format(str(voucherid)))
    qr.save('app/static/qr/voucherqr{}.jpeg'.format(str(voucherid)), "JPEG")
    return render_template('voucherqr.html', data=voucher)

@app.route('/voucher/<int:voucherid>')
@login_required
def voucher(voucherid):
    buy_form=BuyForm()
    voucherData = Vouchercat.query.filter_by(id=voucherid).first()
    return render_template('voucher.html', voucherData=voucherData, buy_form=buy_form)

@app.route('/elements')
@login_required
def elements():
    return render_template('elements.html')

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

@app.route("/cashier/scanQR/<int:voucherid>")
@login_required
def voucherclaim(voucherid):
    voucher = Voucher.query.filter_by(id = voucherid).first()
    date = datetime.datetime(1970,1,1,0,0) + datetime.timedelta(voucher.expiry - 1)
    if voucher.cashiername==current_user.username and voucher.status==1:
        reply = {'photo':current_user.photo ,'cashiername':voucher.cashiername,'value':voucher.value,'expiry':date.strftime("%d-%b-%Y")}
        return make_response(jsonify(reply), 200) 
    elif voucher.cashiername!=current_user.username:
        reply={'status':'wrong store'}
        return make_response(jsonify(reply),469)
    elif voucher.status==0:
        reply={'status':'voucher expired'}
        return make_response(jsonify(reply),469)
    elif voucher.status==1:
        reply={'status':'voucher used alr'}
        return make_response(jsonify(reply),469)        

