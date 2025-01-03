# models.py
from . import db  # Import db object from __init__.py
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)  # Username field
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email field
    password = db.Column(db.String(200), nullable=False)  # Password field
    role = db.Column(db.Integer, default=1) # 0 for admin, 1 for normal user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, default=1) # 0 for success, 1 for pending, 2 for reject
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign Key to User

    user = db.relationship('User', backref=db.backref('tickets', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Ticket {self.title}>'
