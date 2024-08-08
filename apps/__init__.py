# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present Wilson635
"""

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from importlib import import_module

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)  # Initialiser Flask-Mail


def register_blueprints(app):
    for module_name in ('authentication', 'home', 'members'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):
    @app.before_first_request
    def initialize_database():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Configuration de Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.webmail.firsttrust.cm'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'wilson.ngahemeni@firsttrust.cm'
    app.config['MAIL_PASSWORD'] = 'Ftsl2003'
    app.config['MAIL_DEFAULT_SENDER'] = 'wilson.ngahemeni@firsttrust.cm'

    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
