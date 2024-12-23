# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present Wilson635
"""
from datetime import datetime, timezone

from flask_login import UserMixin
import uuid
from apps import db, login_manager
from apps.authentication.util import hash_pass


class Users(db.Model, UserMixin):
    __tablename__ = 'Users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(64), unique=False)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    firstName = db.Column(db.String(64), unique=False)
    lastName = db.Column(db.String(64), unique=False)
    address = db.Column(db.String(64), unique=False)
    city = db.Column(db.String(64), unique=False)
    country = db.Column(db.String(64), unique=False)
    postalCode = db.Column(db.String(64), unique=False)
    about = db.Column(db.Text)
    position = db.Column(db.String(64), unique=False)
    role = db.Column(db.String(64), unique=False)

    def __init__(self, **kwargs):
        for PROPERTY, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if PROPERTY == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, PROPERTY, value)

    def __repr__(self):
        return str(self.username)


class Status(db.Model):
    __tablename__ = 'Status'

    idStatus = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), unique=True, nullable=False)

    def __repr__(self):
        return '<Status %r>' % self.name


class Members(db.Model):
    __tablename__ = 'Members'

    idMember = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), unique=False, nullable=False)
    firstName = db.Column(db.String(64), nullable=False)
    local = db.Column(db.String(64), nullable=False)
    familySituation = db.Column(db.String(64), nullable=False)
    occupation = db.Column(db.String(64), nullable=False)
    dateBirth = db.Column(db.DateTime)
    status_id = db.Column(db.Integer, db.ForeignKey('Status.idStatus'))
    children = db.relationship('Children', backref='member', lazy=True)
    parents = db.relationship('Parents', backref='member', lazy=True)
    partners = db.relationship('Partners', backref='member', lazy=True)
    emergency_contacts = db.relationship('EmergencyContact', backref='member', lazy=True)
    pdf_files = db.relationship('PDFFile', backref='member', lazy=True)

    def __repr__(self):
        return '<Members %r>' % self.name


class Children(db.Model):
    __tablename__ = 'Children'

    idChild = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), nullable=False)
    firstName = db.Column(db.String(64), nullable=False)
    dateBirth = db.Column(db.DateTime)
    member_id = db.Column(db.Integer, db.ForeignKey('Members.idMember'))

    def __repr__(self):
        return '<Children %r>' % self.name


class Parents(db.Model):
    __tablename__ = 'Parents'

    idParent = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), nullable=False)
    firstName = db.Column(db.String(64), nullable=False)
    mobileNumber = db.Column(db.String(20), nullable=False)
    member_id = db.Column(db.String(36), db.ForeignKey('Members.idMember'))

    def __repr__(self):
        return '<Parents %r>' % self.name


class Partners(db.Model):
    __tablename__ = 'Partners'

    idPartner = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), nullable=False)
    firstName = db.Column(db.String(64), nullable=False)
    dateBirth = db.Column(db.DateTime)
    member_id = db.Column(db.String(36), db.ForeignKey('Members.idMember'))

    def __repr__(self):
        return '<Partners %r>' % self.name


class EmergencyContact(db.Model):
    __tablename__ = 'EmergencyContact'

    idEmergency = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(64), nullable=False)
    firstName = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    mobileNumber = db.Column(db.String(20), nullable=False)
    quality = db.Column(db.String(64), nullable=False)
    others = db.Column(db.String(128), nullable=True)
    member_id = db.Column(db.String(36), db.ForeignKey('Members.idMember'))

    def __repr__(self):
        return '<EmergencyContact %r>' % self.name


class PDFFile(db.Model):
    __tablename__ = 'PDFFile'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(120), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    member_id = db.Column(db.String(36), db.ForeignKey('Members.idMember'), nullable=False)

    def __repr__(self):
        return '<PDFFile %r>' % self.filename


class Declaration(db.Model):
    __tablename__ = 'declarations'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('Users.id'), nullable=False)
    member_id = db.Column(db.String(36), db.ForeignKey('Members.idMember'), nullable=False)
    declaration_type = db.Column(db.String(20), nullable=False)  # Détermine le type spécifique de déclaration
    declaration_text = db.Column(db.Text, nullable=True)
    statut = db.Column(db.String(20), nullable=False, default='pending')  # Statut par défaut : "pending"
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Relations
    user = db.relationship('Users', backref=db.backref('declarations', lazy=True))
    member = db.relationship('Members', backref=db.backref('declarations', lazy=True))
    files = db.relationship('DeclarationFile', backref=db.backref('declarations', lazy=True))

    # Définir l'héritage avec le champ polymorphic_on
    __mapper_args__ = {
        'polymorphic_identity': 'declaration',
        'polymorphic_on': declaration_type
    }

    def __repr__(self):
        return f'<Declaration {self.id}>'


# Déclaration pour décès
class DeathDeclaration(Declaration):
    __tablename__ = 'death_declarations'
    id = db.Column(db.String(36), db.ForeignKey('declarations.id'), primary_key=True)
    loss_type = db.Column(db.String(20), nullable=True)  # Type de perte (ex : "father", "spouse")
    deceased_name = db.Column(db.String(64), nullable=True)
    deceased_first_name = db.Column(db.String(64), nullable=True)
    date_of_death = db.Column(db.DateTime, nullable=True)
    cause_of_death = db.Column(db.Text, nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'death'
    }

    def __repr__(self):
        return f'<DeathDeclaration {self.id}>'


# Déclaration pour naissance
class BirthDeclaration(Declaration):
    __tablename__ = 'birth_declarations'
    id = db.Column(db.String(36), db.ForeignKey('declarations.id'), primary_key=True)
    child_name = db.Column(db.String(64), nullable=True)
    child_first_name = db.Column(db.String(64), nullable=True)
    birth_date = db.Column(db.DateTime, nullable=True)
    birth_place = db.Column(db.String(128), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'birth'
    }

    def __repr__(self):
        return f'<BirthDeclaration {self.id}>'


# Déclaration pour mariage
class WeddingDeclaration(Declaration):
    __tablename__ = 'wedding_declarations'
    id = db.Column(db.String(36), db.ForeignKey('declarations.id'), primary_key=True)
    spouse_name = db.Column(db.String(64), nullable=True)
    spouse_first_name = db.Column(db.String(64), nullable=True)
    wedding_date = db.Column(db.DateTime, nullable=True)
    wedding_place = db.Column(db.String(128), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'wedding'
    }

    def __repr__(self):
        return f'<WeddingDeclaration {self.id}>'


# Fichier associé à une déclaration
class DeclarationFile(db.Model):
    __tablename__ = 'DeclarationFiles'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    declaration_id = db.Column(db.String(36), db.ForeignKey('declarations.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_data = db.Column(db.LargeBinary)

    def __repr__(self):
        return f'<DeclarationFile {self.id}>'


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
