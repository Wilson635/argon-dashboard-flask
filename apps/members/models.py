# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present Wilson635
"""
from apps import db, login_manager


class Members(db.Model):
    __tablename__ = 'Members'

    idMember = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    familySituation = db.Column(db.String(64), unique=True, nullable=False)
    occupation = db.Column(db.String(64), unique=True, nullable=False)
    dateBirth = db.Column(db.DateTime, unique=True)
    children = db.relationship('Children', backref='members')

    def __repr__(self):
        return '<Members %r>' % self.name


class Children(db.Model):
    __tablename__ = 'Children'

    idChild = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    firstName = db.Column(db.String(64), unique=True, nullable=False)
    dateBirth = db.Column(db.DateTime, unique=True)
    member_id = db.Column(db.Integer, db.ForeignKey(Members.idMember))

    def __repr__(self):
        return '<Children %r>' % self.name


@login_manager.member_loader
def member_loader(id):
    return Members.query.filter_by(idMember=id).first()


@login_manager.request_loader
def request_loader(request):
    name = request.form.get('name')
    member = Members.query.filter_by(name=name).first()
    return member if member else None
