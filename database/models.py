from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable = False)
    imap_password = db.Column(db.Text, nullable = False)

    subscriptions = db.relationship('Subscription', backref='owner', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)      
    logo_url = db.Column(db.String(255))                
    sender_email = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(120),nullable=False)

    search_keywords = db.Column(db.String(255), nullable = True, default = "оплата, чек, подписка")

class Subscription(db.Model):
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key = True)

    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, default=datetime.utcnow)
    end_date = db.Column(db.Date, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    clicks = db.Column(db.Integer, default = 0)
    category = db.Column(db.String(120), nullable=True)

    service = db.relationship('Service', backref='subscriptions')