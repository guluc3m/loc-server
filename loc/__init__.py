# -*- coding: utf-8 -*-
#
# League of Code server implementation
# https://github.com/guluc3m/loc-server
#
# The MIT License (MIT)
#
# Copyright (c) 2017 Grupo de Usuarios de Linux UC3M <http://gul.es>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Application bootstrap."""

from flask import Flask, make_response
from flask_babel import Babel
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from loc.bootstrap import BASE_CONFIG, make_celery

import os


__version__ = '0.1.0'
__api__versions__ = ['v1']


app = Flask(__name__, instance_relative_config=True)
app.config.update(BASE_CONFIG)

# Load configuration specified in environment variable or default
# development one
# Production configurations shold be stored in `instance/` (ignored in repo)
if 'LOC_CONFIG_FILE' in os.environ:
    app.config.from_envvar('LOC_CONFIG_FILE')

else:
    app.config.from_object('config.development')


# Setup database
db = SQLAlchemy(app)
# Force model registration
from loc import models

# Database migrations
migrate = Migrate(app, db)


# Setup Flask-Babel
babel = Babel(app)


# Setup Flask-Mail
mail = Mail(app)


# Setup Celery
celery = make_celery(app)

# Import celery tasks
from loc.tasks import async_mail


# Blueprints
from loc.endpoints import common_endpoints
from loc.endpoints.v1.account import v1_account
from loc.endpoints.v1.matches import v1_matches
from loc.endpoints.v1.parties import v1_parties
from loc.endpoints.v1.users import v1_users
from loc.endpoints.v1.admin import v1_admin

app.register_blueprint(common_endpoints)
app.register_blueprint(v1_account, url_prefix='/v1/account')
app.register_blueprint(v1_matches, url_prefix='/v1/matches')
app.register_blueprint(v1_parties, url_prefix='/v1/parties')
app.register_blueprint(v1_admin, url_prefix='/v1/admin')

# Cli commands
from loc import cli

@app.route('/')
def root():
    content = (
        'League of Code server - by GUL UC3M\n\n'
        'Version: %s\n'
        'Supported API versions: %s'
    ) % (__version__, ', '.join(__api__versions__))

    response = make_response(content)
    response.headers['content-type'] = 'text/plain'

    return response
