from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from ..app import db


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer(), primary_key=True)
    username = Column(String(128), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    posts = relationship('Post', backref='users', lazy=True)
    comments = relationship('Comment', backref='users', lazy=True)

    def set_hash_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
