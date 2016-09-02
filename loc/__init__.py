# -*- coding: utf-8 -*-

"""Application bootstrap."""

from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from loc.helper.extra import make_celery

import os

app = Flask(__name__, instance_relative_config=True)

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


# Setup Flask-Mail
mail = Mail(app)


# Setup Celery
celery = make_celery(app)


# Blueprints
from loc.views.profile import bp_profile
from loc.views.session import bp_session
from loc.views.user import bp_user

app.register_blueprint(bp_profile)
app.register_blueprint(bp_session)
app.register_blueprint(bp_user)
