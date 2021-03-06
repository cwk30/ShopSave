from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, IntegerField, DateField, SubmitField, BooleanField, TextAreaField, RadioField, SelectField
from wtforms.validators import Required, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import (User, Voucher, Vouchercat)
from flask_login import current_user


class UserRegistrationForm(FlaskForm):
    username =  StringField("Username", validators=[Required(), Length(min=2, max=20)])
    #name =  StringField("Name", validators=[Required(), Length(min=1, max=40)]) 

    email = StringField('Email', validators=[Required(), Email()]) 
    password = PasswordField('Password', validators=[Required()])
    #contactno = StringField('Contact No.', validators=[Required(), Length(min=8, max=8)]) 

    confirm_password = PasswordField('Confirm Password', validators=[Required(), EqualTo('password')])

    submit = SubmitField('Sign Up') 

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first() 
        if user:
            raise ValidationError('That username is already registered. Please choose another.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first() 
        if user:
            raise ValidationError('That email is already registered. Please login with your registered account.')

class UserLoginForm(FlaskForm):
    username =  StringField("Username", validators=[Required(), Length(min=2, max=20)]) 

    password = PasswordField('Password', validators=[Required()])

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login') 

class UserUpdateAccountForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Email()]) 

    password = PasswordField('Password', validators=[Required()]) 
    confirm_password = PasswordField('Confirm Password', validators=[Required(), EqualTo('password')])

    submit = SubmitField('Update') 

class UpdateAccountForm(FlaskForm):
    
    address = StringField("Address", validators=[]) 
    password = PasswordField('Password*', validators=[Required()]) 
    confirm_password = PasswordField('Confirm Password*', validators=[Required(), EqualTo('password')])
    photo = FileField('Upload Photo', validators=[FileAllowed(['jpg', 'png'])])
    contactno = IntegerField("Contact No.*", validators=[])
    
    submit = SubmitField('Update') 

    def validate_contactno(self, contactno):
        user = User.query.filter_by(contactno=contactno.data).first() 
        if user and contactno!=current_user.contactno:
            raise ValidationError('That contact no is already registered. Please choose another.')    

class CashierRegistrationForm(FlaskForm):
    username =  StringField("Business Name", validators=[Required(), Length(min=2, max=20)])
    #name =  StringField("Name", validators=[Required(), Length(min=1, max=40)]) 

    email = StringField('Business Email', validators=[Required(), Email()]) 
    password = PasswordField('Password', validators=[Required()])
    #contactno = StringField('Contact No.', validators=[Required(), Length(min=8, max=8)]) 

    confirm_password = PasswordField('Confirm Password', validators=[Required(), EqualTo('password')])

    submit = SubmitField('Sign Up') 
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first() 
        if user:
            raise ValidationError('That email is already registered. Please login with your registered account.')

class CashierLoginForm(FlaskForm):
    username =  StringField("Username", validators=[Required(), Length(min=2, max=20)]) 

    password = PasswordField('Password', validators=[Required()])

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login') 

class BuyForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[Required()])

    submit = SubmitField('Buy')
    # def validate_purchase(self, qtyBought, voucherId):
    #     qtyAvailable = Vouchercat.query.filter_by(id=voucherId).first().quantity
    #     if qtyAvailable<qtyBought:
    #         errorMessage = "Not able to purchase " + str(qtyBought) + " vouchers. Only " + str(qtyAvailable) + " vouchers available."
    #         raise ValidationError(errorMessage)

class CheckoutForm(FlaskForm):
    nameOnCard = StringField('Name on card', validators=[Required()])
    creditCardNumber = IntegerField('Credit Card Number', validators=[Required()])
    expirationMonth = IntegerField("Expiration Month (MM)", validators=[Required()])
    expirationYear = IntegerField("Expiration Year (YYYY)", validators=[Required()])
    cvv = IntegerField("CVV", validators=[Required()])
    submit = SubmitField('Buy')

class VoucherUpdate(FlaskForm):
    value = IntegerField("Voucher Value", validators=[Required()])
    transfer = BooleanField('Transferable?')
    cost = IntegerField("Cost Price", validators=[Required()])
    expirydur = IntegerField("Expiry Duration", validators=[Required()])
    quantity = IntegerField("Quantity", validators=[Required()])
    submit = SubmitField('Update')
    
class VoucherCreate(FlaskForm):
    value = IntegerField("Voucher Value", validators=[Required()])
    transfer = BooleanField('Transferable?')
    cost = IntegerField("Cost Price", validators=[Required()])
    expirydur = IntegerField("Expiry Duration", validators=[Required()])
    quantity = IntegerField("Quantity", validators=[Required()])
    submit = SubmitField('Create')

