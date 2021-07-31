from flask_wtf import FlaskForm 
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField, SelectField
from wtforms.validators import Required, Length, Email, EqualTo, ValidationError
from app.models import (User)
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