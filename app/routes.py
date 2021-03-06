import secrets
import os
from PIL import Image 
from flask_login.mixins import UserMixin
from app import app, db, bcrypt, login_manager
from flask import (render_template, jsonify, make_response, url_for, flash, redirect, request, abort, session)
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_, and_, select, create_engine
from flask_sqlalchemy import Pagination
from app.forms import (UserRegistrationForm, VoucherUpdate, VoucherCreate, UserLoginForm, BuyForm, UpdateAccountForm, CashierRegistrationForm, CashierLoginForm, CheckoutForm)
from app.models import (User, Voucher, Vouchercat)
from flask import request
import qrcode
import datetime
from collections import defaultdict, OrderedDict

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
    # distinct_cashiers = []
    # for i in range(len(data)):
    #     if data[i].cashiername not in distinct_cashiers:
    #         distinct_cashiers.append(data[i].cashiername)
    # join = Vouchercat.query.join(User, Vouchercat.cashiername==User.username, isouter=True).all()
    # return render_template('test.html', data=join)

    # voucher_data = Voucher.query.filter_by(username = current_user.username).all()
    unique_cashier_freq = {}
    for i in range(len(data)):
        if data[i].cashiername not in unique_cashier_freq:
            unique_cashier_freq[data[i].cashiername] = 1
        else:
            unique_cashier_freq[data[i].cashiername] += 1
    positions = []
    for name, count in unique_cashier_freq.items():
        user = User.query.filter_by(username = name).first()
        user_pic = user.photo
        positions.append((name,count,user_pic))
    return render_template('userlanding.html', data=positions)

@app.route('/user/voucherstore/<string:cashiername>',methods=['GET', 'POST'])
@login_required 
def uservoucherstore(cashiername):
    vouchers_on_sale = Vouchercat.query.filter_by(cashiername = cashiername).all()
    if len(vouchers_on_sale) > 0:
        user = User.query.filter_by(username = vouchers_on_sale[0].cashiername).first()
        user_pic = user.photo
        return render_template('uservoucherstore.html', data=vouchers_on_sale, name = cashiername, user_pic=user_pic)
    else:
        emptyMessage = "This store has no vouchers for sale."
        return render_template('uservoucherstore.html', data=vouchers_on_sale, name = cashiername, emptyMessage=emptyMessage)
    # return render_template('test.html', data=data)

@app.route('/user/voucherwallet', methods=['GET', 'POST'])
@login_required
def uservoucherwallet():
    voucher_data = Voucher.query.filter_by(username = current_user.username, status = 1).all()
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
        user = User.query.filter_by(username = key).all()
        user_pic = user[0].photo
        positions.append((key,value,count,user_pic))
        count = count + 1
    if len(unique_cashier_freq) == 0 :
        return render_template('emptywallet.html')
    else:
        return render_template('wallet.html', data=positions, value = len(positions))

@app.route('/user/voucherwallet/<string:cashiername>',methods=['GET', 'POST'])
@login_required 
def uservoucher(cashiername):
    vouchers_owned = Voucher.query.filter_by(username = current_user.username, cashiername=cashiername, status = 1).all()
    if len(vouchers_owned) > 0:
        user = User.query.filter_by(username = vouchers_owned[0].cashiername).all()
        user_pic = user[0].photo
        return render_template('uservoucher.html', data=vouchers_owned, user_pic = user_pic)
    else:
        return render_template('emptyvoucher.html', data=cashiername, available = 1)

@app.route('/user/voucherwallet/<string:cashiername>/unavailable',methods=['GET', 'POST'])
@login_required 
def unavailablevoucher(cashiername):
    unavailable_vouchers = Voucher.query.filter(Voucher.status != 1, Voucher.username == current_user.username, Voucher.cashiername==cashiername).all()
    if len(unavailable_vouchers) == 0 :
        return render_template('emptyvoucher.html', data=cashiername, available = 0)
    else:
        user = User.query.filter_by(username = unavailable_vouchers[0].cashiername).all()
        user_pic = user[0].photo
        return render_template('user_unavailable_voucher.html', data=unavailable_vouchers, user_pic = user_pic)

@app.route('/user/voucherwallet/<int:voucherid>',methods=['GET', 'POST'])
@login_required 
def voucherqr(voucherid):
    voucher = Voucher.query.filter_by(id = voucherid)
    qr = qrcode.make('{}'.format(str(voucherid)))
    filePath = 'static/qr/voucherqr{}.jpeg'.format(str(voucherid))
    qr.save("app/" + filePath, "JPEG")
    reply={'filePath': filePath}
    return make_response(jsonify(reply), 200)

@app.route('/voucher/<int:voucherid>', methods=['GET', 'POST'])
@login_required
def voucher(voucherid):
    buy_form=BuyForm()
    voucherData = Vouchercat.query.filter_by(id=voucherid).first()
    cashier = User.query.filter_by(username = voucherData.cashiername).first()
    cashier_pic = cashier.photo
    if buy_form.validate_on_submit():
        voucherData = Vouchercat.query.filter_by(id=voucherid).first()       
        quantity = buy_form.quantity.data
        if 0 < quantity <= voucherData.quantity:
            session['voucherID'] = voucherData.id
            session['quantity'] = quantity
            return redirect(url_for('checkout'))
        else:
            errorMessage = "Not able to purchase " + str(quantity) + " vouchers. Only " + str(voucherData.quantity) + " vouchers available."
            return render_template('voucher.html', voucherData=voucherData, buy_form=buy_form, cashier_pic=cashier_pic, errorMessage=errorMessage)
    return render_template('voucher.html', voucherData=voucherData, buy_form=buy_form, cashier_pic=cashier_pic)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    voucherId = session['voucherID']
    quantity = session['quantity']
    coForm = CheckoutForm()
    if request.method == 'GET':
        coForm.nameOnCard.data = "John Davis"
        coForm.creditCardNumber.data = 4119528685973112
        coForm.expirationMonth.data = 12
        coForm.expirationYear.data = 2024
        coForm.cvv.data = 621
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
        today_epoch = datetime.datetime(today.year,today.month,today.day) - datetime.datetime(1970,1,1) + datetime.timedelta(days=1)
        vouchercat.quantity = vouchercat.quantity - quantity
        vouchercat.sold = vouchercat.sold + quantity
        
        for i in range(quantity):
            db.session.add(Voucher(username=session["username"], cashiername=vouchercat.cashiername, expiry=epoch_day.days, value=vouchercat.value, transfer=vouchercat.transfer, status=1, expirydate=expirydate, sold=today_epoch.days))
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
    voucherdata = Voucher.query.filter_by(cashiername=cashier)
    chartDic = defaultdict(int)
    for i in voucherdata:
        soldEpoch = i.sold
        soldDate = datetime.datetime(1970,1,1,0,0) + datetime.timedelta(soldEpoch - 1)
        month = soldDate.month
        year = soldDate.year
        VC = Vouchercat.query.filter_by(value=i.value, cashiername=cashier).first()
        if VC is not None:
            cost = VC.cost
            chartDic[month] += cost
        # print(cost)
        # if year not in chartDic:
        #     chartDic[year] = {}
        # if month not in chartDic[year]:
        #     chartDic[year][month] = cost
        # else:
        #     chartDic[year][month] += cost
    # chartDic = dict(sorted(chartDic.items()))
    chartDic=  OrderedDict(sorted(chartDic.items()))
    # return render_template('test.html', data=chartDic)
    chartList =[]
    # for year, yeardict in chartDic.items():
    #     for month, cost in yeardict.items():
    #         chartList.append( [year, month ,chartDic[year][month]])
    # chartList = sorted()

    # print(chartList)
    chartList.append(["Month", "Revenue"])
    for key, value in chartDic.items():
        temp = [key,value]
        chartList.append(temp)

    return render_template('cashierlanding.html', revenue=revenue, sold=sold, vouchers=cashierdata, chartList=chartList)

@app.route('/cashier/manage_vouchers',methods=['GET', 'POST'])
@login_required
def manageVouchers():
    cashier = session["username"]
    voucherdata = Vouchercat.query.filter_by(cashiername=cashier).all()
    # for i in range(len(voucherdata)):
    #     data.append((voucherdata[i], str(voucherdata[i].id)))
    # voucherkeys = [str(voucher.id) for voucher in voucherdata]
    if len(voucherdata) == 0:
        message = "Your business has no voucher yet. Create some vouchers now!"
        return render_template('cashiervoucher.html', vouchers=voucherdata, alert=message)
    return render_template('cashiervoucher.html', vouchers=voucherdata)


@app.route('/voucher/update/<int:voucherid>', methods=['GET', 'POST'])
@login_required
def voucherUpdate(voucherid):
    voucherUpdateForm = VoucherUpdate()
    voucherData = Vouchercat.query.filter_by(id=voucherid).first()
    if request.method == 'GET':
        voucherUpdateForm.value.data = voucherData.value
        voucherUpdateForm.cost.data = voucherData.cost
        voucherUpdateForm.expirydur.data = voucherData.expirydur
        voucherUpdateForm.quantity.data = voucherData.quantity

    if voucherUpdateForm.validate_on_submit():

        voucherData.value = voucherUpdateForm.value.data
        voucherData.cost = voucherUpdateForm.cost.data
        voucherData.expirydur = voucherUpdateForm.expirydur.data
        voucherData.quantity = voucherUpdateForm.quantity.data
        voucherData.transfer = 0

        db.session.commit()
        flash('Your voucher has been updated', 'success')

    return render_template('voucherupdate.html', voucherData=voucherData, updateform=voucherUpdateForm)

@app.route('/cashier/voucher/create',methods=['GET','POST'])
@login_required
def voucherCreate():
    voucherCreateForm = VoucherCreate()
    if voucherCreateForm.validate_on_submit():
        vouchercat = Vouchercat(value=voucherCreateForm.value.data, transfer=0, cost=voucherCreateForm.cost.data,expirydur=voucherCreateForm.expirydur.data, quantity=voucherCreateForm.quantity.data, cashiername=session['username'], sold=0)
        db.session.add(vouchercat)
        db.session.commit()
        flash('Your voucher has been created', 'success')
    return render_template('vouchercreate.html', form=voucherCreateForm) 
    
@app.route('/voucher/delete/<int:voucherid>', methods=['GET', 'POST'])
@login_required
def voucherDelete(voucherid):
    # Send back to cashiervouchers.html with an alert
    cashier = session["username"]
    voucherdata = Vouchercat.query.filter_by(cashiername=cashier).all()
    voucherDeleted = Vouchercat.query.filter_by(id=voucherid).first()
    voucherDelete = Vouchercat.query.filter_by(id=voucherid).delete()
    alertMessage = "Voucher has been deleted"
    db.session.commit()

    return render_template('cashiervoucher.html', vouchers=voucherdata, alert=alertMessage)    

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
        voucher.status=2
        db.session.commit()
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

# @app.errorhandler(Exception)
# def server_error(err):
#     app.logger.exception(err)
#     return unauthorized_callback()

# @app.route('/develop')
# #@login_required
# def develop():
#     return render_template('card.html')