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
    username = db.Column(db.String(64), unique=False)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    role = db.Column(db.String(64), unique=False)

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


class Status(db.Model):
    __tablename__ = 'Status'

    idStatus = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return '<Status %r>' % self.name


class Roles(db.Model):
    __tablename__ = 'Roles'

    idRole = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return '<Roles %r>' % self.name


class Members(db.Model):
    __tablename__ = 'Members'

    idMember = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False, nullable=False)
    familySituation = db.Column(db.String(64), nullable=False)
    occupation = db.Column(db.String(64), nullable=False)
    dateBirth = db.Column(db.DateTime)
    status_id = db.Column(db.Integer, db.ForeignKey('Status.idStatus'))
    role_id = db.Column(db.Integer, db.ForeignKey('Roles.idRole'))
    children = db.relationship('Children', backref='member')

    def __repr__(self):
        return '<Members %r>' % self.name


class Children(db.Model):
    __tablename__ = 'Children'

    idChild = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    firstName = db.Column(db.String(64), nullable=False)
    dateBirth = db.Column(db.DateTime)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.idMember'))

    def __repr__(self):
        return '<Children %r>' % self.name


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
