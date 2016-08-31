# -*- coding: utf-8 -*-

"""Application bootstrap."""

from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from loc.helper.extra import make_celery

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# Register models
from loc import models
db.create_all()


# Setup Flask-Mail
mail = Mail(app)


# Setup Celery
celery = make_celery(app)
