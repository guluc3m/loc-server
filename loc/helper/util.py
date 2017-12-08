# -*- coding: utf-8 -*-

"""Utility functions."""

from flask import jsonify, current_app
from loc import db
from loc.helper import messages as m
from loc.models import User

import datetime
import random
import bcrypt
import jwt


def api_error(message='', **kwargs):
    """Generate an error JSON response.

    This response is based on the JSend specification and should be used when
    there is an API call fails due to an error processing the request.

    Keyword arguments are included in the 'data' attribute of the response. This
    attribute is optional.

    Args:
        message (str): Message to include in the response
    """
    response = {
        'status': 'error',
        'message': message
    }

    if kwargs:
        response['data'] = kwargs

    return jsonify(**response)

def api_fail(*args, **kwargs):
    """Generate a failure JSON response.

    This response is based on the JSend specification and should be used when
    the data received is invalid.

    Arguments are included in the 'data' attribute of the response, with *args
    taking preference over **kwargs.
    """
    response = {
        'status': 'fail',
        'data': list(args) or kwargs
    }

    return jsonify(**response)

def api_success(*args, **kwargs):
    """Generate a success JSON response.

    This response is based on the JSend specification.

    Arguments are included in the 'data' attribute of the response, with *args
    taking preference over **kwargs.
    """
    response = {
        'status': 'success',
        'data': list(args) or kwargs
    }

    return jsonify(**response)

def check_missing_fields(data, ignore=[]):
    """Check for missing fields in the provided data.

    Args:
        data (dict): dict of data received in the API
        ignore (list[str]): list of keys to ignore when checking required fields

    Returns:
        dict with missing fields as keys and error message as value
    """
    error = {}

    for field, value in data.items():
        if field not in ignore and not value:
            error[field] = m.FIELD_MISSING

    return error

def generate_expiration_date(**kwargs):
    """Generate an expiration date starting on current UTC datetime.

    Arguments correspond to those of the `datetime.timedelta()` function.
    """
    return datetime.datetime.utcnow() + datetime.timedelta(**kwargs)

def generate_token(length=32):
    """Generate a random token.

    Args:
        length (int): Number of characters in the token.

    Returns:
        Random character sequence.
    """
    _allowed = 'abcdefghijklmnoprstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-_$'
    token = ''.join(random.SystemRandom().choice(_allowed) for i in range(length))

    return token

def hash_matches(password, hashed):
    """Check a password against a hash.

    Uses bcrypt algorithm.

    Args:
        password (str): Original password.
        hashed (str): Hashed password.

    Returns:
        `True` or `False`
    """
    # Bcrypt works with bytes
    return bcrypt.checkpw(password.encode(), hashed.encode())

def hash_password(password):
    """Hash the provided password.

    Uses bcrypt algorithm.

    Args:
        password (str): Plaintext password.

    Returns:
        Hashed password.
    """
    # Bcrypt works with bytes
    rounds = current_app.config.get('BCRYPT_ROUNDS', 12)

    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(rounds=rounds)
    ).decode()

def record_exists(model, **kwargs):
    """Check if a record exists using a simple filter.

    Kwargs are used to create the filter.

    Args:
        model (Model): Database model to query.
    """
    return db.session.query(
        model
        .query
        .filter_by(**kwargs)
        .exists()
    ).scalar()

def user_from_jwt(token):
    """Obtain user record from JWT token.

    Args:
        token (str): Encoded JWT token.

    Returns:
        `User` record if it exists, otherwise `None`.
    """
    # Decode
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'])

    except jwt.ExpiredSignatureError:
        #TODO log
        return None

    # Get user
    return User.query.filter_by(
        id=decoded.get('sub', -1),
        is_deleted=False
    ).first()
