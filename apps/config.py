# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present Wilson635
"""

import os
from decouple import config


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'mutual.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.webmail.firsttrust.cm'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'wilson.ngahemeni@firsttrust.cm'
    MAIL_PASSWORD = 'Ftsl2003'
    MAIL_DEFAULT_SENDER = 'wilson.ngahemeni@firsttrust.cm'


class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgresSQL database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        config('DB_ENGINE', default='postgresql'),
        config('DB_USERNAME', default='postgres'),
        config('DB_PASS', default='wilson715'),
        config('DB_HOST', default='localhost'),
        config('DB_PORT', default=5432),
        config('DB_NAME', default='mutuelle-ftsl')
    )


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
