# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present Wilson635
"""
from apps import db


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