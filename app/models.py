from app import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Voucher(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable=False)
    cashiername = db.Column(db.String(20), nullable=False)
    expiry = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    transfer = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)

class VoucherCat(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    value = db.Column(db.Integer, nullable=False)
    transfer = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    expirydur = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    cashiername = db.Column(db.String(20), unique=True, nullable=False)
    sold = db.Column(db.Integer, nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True) 
    username = db.Column(db.String(20), unique=True, nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    cashier = db.Column(db.Integer, nullable=False)
    contactno = db.Column(db.Integer)
    dateofbirth = db.Column(db.Integer)
    photo = db.Column(db.String)
    address = db.Column(db.String)

    #def get_reset_token(self, expires_sec=1800):
    #    s = Serializer(app.config['SECRET_KEY'], expires_sec)
    #    return s.dumps({'user_id': self.id}).decode('utf-8')

    #@staticmethod 
    #def verify_reset_token(token):
    #    s = Serializer(app.config['SECRET_KEY'])
    #    try:
    #        userid = s.loads(token)['user_id']
    #    except:
    #        return None
    #    return User.query.get(username)


    def __repr__(self): 
        return f"User('{self.username}', '{self.email}')"