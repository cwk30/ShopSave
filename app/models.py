from app import db, login_manager, app
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(username):
    return User.query.get(int(username))

class User(db.Model, UserMixin):
    username = db.Column(db.Integer, primary_key = True) 
    #name = db.Column(db.String(20), unique=True, nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    #contactno = db.Column(db.Integer)

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