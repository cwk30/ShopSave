import secrets
import os
from PIL import Image 
from flask_login.mixins import UserMixin
from app import app, db, bcrypt, login_manager
from flask import (render_template, jsonify, make_response, url_for, flash, redirect, request, abort, session)
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_, and_, select, create_engine
from flask_sqlalchemy import Pagination
from app.forms import (UserRegistrationForm, UserLoginForm, BuyForm, UpdateAccountForm, CashierRegistrationForm, CashierLoginForm, CheckoutForm)
from app.models import (User, Voucher, Vouchercat)
from flask import request
import qrcode
import datetime

def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')

@app.route("/trailer")
def trailer():
    return redirect('https://www.youtube.com/watch?v=LGkUW5cUPz8')

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
        user = User(username=userregister_form.username.data, password=hashed_password,email=userregister_form.email.data,cashier=0,photo="img.png")
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", 'success') 
        return redirect('/user#login')
    if userlogin_form.validate_on_submit():
        user = User.query.filter_by(username=userlogin_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, userlogin_form.password.data) and user.cashier==0:
            login_user(user, remember=userlogin_form.remember.data)
            next_page = request.args.get('next')
            session["username"]=user.username
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
        user = User(username=cashierregister_form.username.data, password=hashed_password,email=cashierregister_form.email.data,cashier=1,photo="temp.jpg")
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", 'success') 
        return redirect('/cashier#login')
    if cashierlogin_form.validate_on_submit():
        user = User.query.filter_by(username=cashierlogin_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, cashierlogin_form.password.data) and user.cashier==1:
            login_user(user, remember=cashierlogin_form.remember.data)
            next_page = request.args.get('next')
            session["username"]=user.username
            return redirect(url_for('cashierhome'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('cashier.html',cashierregister_form=cashierregister_form, cashierlogin_form=cashierlogin_form)

@app.route('/user/home',methods=['GET', 'POST'])
@login_required 
def userhome():
    data = Vouchercat.query.filter(Vouchercat.quantity>0).all()
    distinct_cashiers = []
    for i in range(len(data)):
        if data[i].cashiername not in distinct_cashiers:
            distinct_cashiers.append(data[i].cashiername)
    # data = Vouchercat.query.join(User, Vouchercat.cashiername==User.username, isouter=True).all()  
    # print(data)
    return render_template('userlanding.html', data=distinct_cashiers)
    # return render_template('test.html', data=data)

@app.route('/user/voucherstore/<string:cashiername>',methods=['GET', 'POST'])
@login_required 
def uservoucherstore(cashiername):
    vouchers_on_sale = Vouchercat.query.filter_by(cashiername = cashiername).all()
    return render_template('uservoucherstore.html', data=vouchers_on_sale, name = cashiername)
    # return render_template('test.html', data=data)

@app.route('/user/voucherwallet', methods=['GET', 'POST'])
@login_required
def uservoucherwallet():
    voucher_data = Voucher.query.filter_by(username = current_user.username).all()
    # distinct_cashiers = []
    # for i in range(len(voucher_data)):
    #     if voucher_data[i].cashiername not in distinct_cashiers:
    #         distinct_cashiers.append(voucher_data[i].cashiername)
    unique_cashier_freq = {}
    for i in range(len(voucher_data)):
        if voucher_data[i].cashiername not in unique_cashier_freq:
            unique_cashier_freq[voucher_data[i].cashiername] = 1
        else:
            unique_cashier_freq[voucher_data[i].cashiername] += 1
    count = 1
    positions = []
    for key, value in unique_cashier_freq.items():
        positions.append((key,value,count))
        count = count + 1
    if len(unique_cashier_freq) == 0 :
        return render_template('emptywallet.html')
    else:
        return render_template('wallet.html', data=positions, value = len(positions))

@app.route('/user/voucherwallet/<string:cashiername>',methods=['GET', 'POST'])
@login_required 
def uservoucher(cashiername):
    vouchers_owned = Voucher.query.filter_by(username = current_user.username, cashiername=cashiername, status = 1).all()
    return render_template('uservoucher.html', data=vouchers_owned)

@app.route('/user/voucherwallet/<string:cashiername>/unavailable',methods=['GET', 'POST'])
@login_required 
def unavailablevoucher(cashiername):
    unavailable_vouchers = Voucher.query.filter(Voucher.status != 1, Voucher.username == current_user.username, Voucher.cashiername==cashiername).all()
    if len(unavailable_vouchers) == 0 :
        return render_template('emptyvoucher.html', data=cashiername)
    else:
        return render_template('user_unavailable_voucher.html', data=unavailable_vouchers)

@app.route('/user/voucherwallet/<int:voucherid>',methods=['GET', 'POST'])
@login_required 
def voucherqr(voucherid):
    voucher = Voucher.query.filter_by(id = voucherid)
    qr = qrcode.make('{}'.format(str(voucherid)))
    filePath = 'static/qr/voucherqr{}.jpeg'.format(str(voucherid))
    qr.save("app/" + filePath, "JPEG")
    reply={'filePath': filePath}
    return make_response(jsonify(reply), 200)

# @app.route('/user/voucherwallet/<string:cashiername>/testing',methods=['GET'])
# @login_required 
# def testing(cashiername):
#     # data = Voucher.query\
#     #     .join(User)\
#     #     .filter_by(Voucher.username==User.username).all()
#     data = select(Voucher).where(
#                 and_(
#                     Voucher.cashiername == 'cashier1',
#                     Voucher.value == 20
#                 )
#             )
#     print(data)
#     engine = create_engine('sqlite:///site.db')
#     with engine.connect() as con:

#         rs = con.execute('SELECT * FROM Voucher')

#     for row in rs:
#         print(row)
#     return render_template('notyet.html')

@app.route('/voucher/<int:voucherid>', methods=['GET', 'POST'])
@login_required
def voucher(voucherid):
    buy_form=BuyForm()
    if buy_form.validate_on_submit():
        voucherData = Vouchercat.query.filter_by(id=voucherid).first()       
        quantity = buy_form.quantity.data
        if quantity <= voucherData.quantity:
            session['voucherID'] = voucherData.id
            session['quantity'] = quantity
            return redirect(url_for('checkout'))
        else:
            errorMessage = "Not able to purchase " + str(quantity) + " vouchers. Only " + str(voucherData.quantity) + " vouchers available."
            return render_template('voucher.html', voucherData=voucherData, buy_form=buy_form, errorMessage=errorMessage)
    voucherData = Vouchercat.query.filter_by(id=voucherid).first()
    return render_template('voucher.html', voucherData=voucherData, buy_form=buy_form)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    voucherId = session['voucherID']
    quantity = session['quantity']
    coForm = CheckoutForm()
    if coForm.validate_on_submit():
        errorMessage=[]
        error = False
        name=coForm.nameOnCard.data
        errorMessage.append("")
        creditCardNumber=coForm.creditCardNumber.data
        if len(str(creditCardNumber))==16 and isinstance(creditCardNumber,int):
            errorMessage.append("")
        else:
            errorMessage.append("Please enter a valid credit card number.")
            error = True
        expiryMonth=coForm.expirationMonth.data
        if expiryMonth>=1 and expiryMonth<=12:
            errorMessage.append("")
        else:
            errorMessage.append("Please enter a valid month")
            error = True
        expiryYear=coForm.expirationYear.data
        if expiryYear>=2021:
            errorMessage.append("")
        else:
            errorMessage.append("Please enter a valid year")
            error = True
        cvv=coForm.cvv.data
        if len(str(cvv))==3 and isinstance(cvv, int):
            errorMessage.append("")
        else:
            errorMessage.append("Please enter a valid cvv number")
            error = True
        if error:
            return render_template('checkout.html', coForm=coForm, errorMessage=errorMessage)
        
        vouchercat = Vouchercat.query.filter_by(id=voucherId).first()
        today = datetime.date.today()
        epoch_day = datetime.datetime(today.year,today.month,today.day) - datetime.datetime(1970,1,1) + datetime.timedelta(days=vouchercat.expirydur+1)
        voucher_expiry_date = datetime.datetime(1970,1,1,0,0) + datetime.timedelta(epoch_day.days - 1)
        expirydate = voucher_expiry_date.strftime("%d-%b-%Y")
        # voucher = Voucher(username=session["username"], cashiername=vouchercat.cashiername, expiry=epoch_day.days, value=vouchercat.value, transfer=vouchercat.transfer, status=1, expirydate=expirydate)
        
        vouchercat.quantity = vouchercat.quantity - quantity
        vouchercat.sold = vouchercat.sold + quantity
        
        for i in range(quantity):
            db.session.add(Voucher(username=session["username"], cashiername=vouchercat.cashiername, expiry=epoch_day.days, value=vouchercat.value, transfer=vouchercat.transfer, status=1, expirydate=expirydate))
        db.session.commit()
        voucher_purchased = Vouchercat.query.filter_by(id = voucherId).all()
        return render_template('purchase_voucher_confirm.html', quantity=quantity, value=voucher_purchased[0].value, cashiername=voucher_purchased[0].cashiername)
        # return redirect(url_for('uservoucherwallet'))
    return render_template('checkout.html', coForm=coForm)

@app.route('/elements')
def elements():
    return render_template('elements.html')

@app.route('/user/userQR')
@login_required
def userQR():
    return render_template('anythinglah.html')

@app.route('/cashier/home',methods=['GET', 'POST'])
@login_required
def cashierhome():
    # data = Vouchercat.query.filter(Vouchercat.quantity>0).all()
    cashier = session["username"]
    cashierdata = Vouchercat.query.filter_by(cashiername=cashier).all()
    revenue = 0
    sold = 0 
    for i in cashierdata:
        revenue += i.sold * i.cost
        sold += i.sold
    chartData = []
    chartData.append(['Month', 'Sales'])
    # voucherdata = Voucher.query.filter_by(cashiername=cashier).order_by(sold)
    # # make a dictionary of month-year
    # epoch_day = datetime.datetime(today.year,today.month,today.day) - datetime.datetime(1970,1,1) + datetime.timedelta(days=vouchercat.expirydur+1)
    # voucher_expiry_date = datetime.datetime(1970,1,1,0,0) + datetime.timedelta(epoch_day.days - 1)

    # # loop through dic. If there is data, add to list.
    # for i in voucherdata:
    #     chartData.append(['', ''])
    chartData=[
		['Month', 'Sales'],
		['Jan',  10],
		['Feb',  11],
		['Mar',  6],
		['Apr',  10]
		]
    return render_template('cashierlanding.html', revenue=revenue, sold=sold, vouchers=cashierdata, chartData=chartData)

@app.route('/cashier/manage_vouchers',methods=['GET', 'POST'])
@login_required
def manageVouchers():
    cashier = session["username"]
    voucherdata = Vouchercat.query.filter_by(cashiername=cashier).all()
    # CHECK WITH WC WHAT DATA HE NEEDS
    return render_template('manageVouchers.html', voucherdata=voucherdata)

@app.route('/voucher/update/<int:voucherid>', methods=['GET', 'POST'])
@login_required
def voucherUpdate(voucherid):
    # buy_form=BuyForm()
    # if buy_form.validate_on_submit():
    #     voucherData = Vouchercat.query.filter_by(id=voucherid).first()       
    #     quantity = buy_form.quantity.data
    #     if quantity <= voucherData.quantity:
    #         session['voucherID'] = voucherData.id
    #         session['quantity'] = quantity
    #         return redirect(url_for('checkout'))
    #     else:
    #         errorMessage = "Not able to purchase " + str(quantity) + " vouchers. Only " + str(voucherData.quantity) + " vouchers available."
    #         return render_template('voucher.html', voucherData=voucherData, buy_form=buy_form, errorMessage=errorMessage)
    # voucherData = Vouchercat.query.filter_by(id=voucherid).first()
    return render_template('voucher.html', voucherData=voucherData, buy_form=buy_form)

@app.route('/voucher/update/<int:voucherid>', methods=['GET', 'POST'])
@login_required
def voucherDelete(voucherid):
    pass

@app.route("/cashier/account", methods=['GET', 'POST'])
@login_required 
def cashierprofile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.photo.data:
            picture_file = save_picture(form.photo.data)
            current_user.photo = picture_file
        current_user.address = form.address.data
        current_user.contactno = form.contactno.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        flash('Your account info has been updated', 'success')
        return redirect(url_for('userprofile'))
    #elif request.method == 'GET':
    image_file = url_for('static', filename='uploads/' + current_user.photo) 
    return render_template('cashierprofile.html', title="Profile", image_file=image_file, form=form)

@app.route("/user/account", methods=['GET', 'POST'])
@login_required 
def userprofile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.photo.data:
            picture_file = save_picture(form.photo.data)
            current_user.photo = picture_file
        current_user.address = form.address.data
        current_user.contactno = form.contactno.data
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        flash('Your account info has been updated', 'success')
        return redirect(url_for('userprofile'))
    #elif request.method == 'GET':
    image_file = url_for('static', filename='uploads/' + current_user.photo) 
    return render_template('userprofile.html', title="Profile", image_file=image_file, form=form)

#TODO: once implemented make it login required
@app.route('/cashier/scanQR')
#@login_required
def cashierqr():
    return render_template('scanqr.html')


@app.route("/user/logout")
@login_required
def logoutuser():
    logout_user()
    session.clear()
    return redirect(url_for('users'))

@app.route("/cashier/logout")
@login_required
def logoutcashier():
    logout_user()
    session.clear()
    return redirect(url_for('cashier'))


#todos:should we check if the login user is a user and not a cashier?
@app.route("/cashier/scanQR/<int:voucherid>", methods=['POST'])
@login_required
def voucherclaim(voucherid):
    voucher = Voucher.query.filter_by(id = voucherid).first()
    if voucher is None: # to prevent exception in datetime.timedelta(voucher.expiry - 1)
        reply={'status':'invalid voucher', 'cashiername':current_user.username}
        return make_response(jsonify(reply), 401)
    date = datetime.datetime(1970,1,1,0,0) + datetime.timedelta(voucher.expiry - 1)
    if voucher.cashiername==current_user.username and voucher.status==1: # check if the same user is doing the purchase
        reply = {'photo':current_user.photo ,'cashiername':voucher.cashiername,'value':voucher.value,'expiry':date.strftime("%d-%b-%Y")}
        return make_response(jsonify(reply), 200) 
    elif voucher.cashiername!=current_user.username: 
        reply={'status':'wrong store', 'cashiername' :current_user.username}
        return make_response(jsonify(reply), 469)
    elif voucher.status == 0:
        reply={'status':'voucher expired','cashiername' :current_user.username}
        return make_response(jsonify(reply), 469)
    elif voucher.status==1:
        reply={'status':'voucher used alr', 'cashiername' :current_user.username}
        return make_response(jsonify(reply), 469)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename) 
    picture_fn = random_hex + f_ext 
    picture_path = os.path.join(app.root_path, 'static/uploads', picture_fn) 
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    
    i.save(picture_path)

    return picture_fn