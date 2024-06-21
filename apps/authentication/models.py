# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present Wilson635
"""

from typing import Any

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass


class Users(db.Model, UserMixin):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    role = db.Column(db.String(64), unique=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Last name of the member
    first_name = db.Column(db.String(100), nullable=False)  # First name of the member
    date_of_birth = db.Column(db.Date, nullable=False)  # Date of birth of the member
    email = db.Column(db.String(100), unique=True, nullable=False)  # Email of the member
    address = db.Column(db.String(200), nullable=False)  # Address of the member
    city = db.Column(db.String(100), nullable=False)  # City of the member
    postal_code = db.Column(db.String(10), nullable=False)  # Postal code of the member
    phone = db.Column(db.String(20), nullable=False)  # Phone number of the member
    member_card_number = db.Column(db.String(20), unique=True, nullable=False)  # Member card number
    join_date = db.Column(db.Date, nullable=False)  # Date when the member joined

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to link with user
    user = db.relationship('Users', backref=db.backref('members', lazy=True))  # Relationship with the user table


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
