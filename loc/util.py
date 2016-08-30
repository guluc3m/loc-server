# -*- coding: utf-8 -*-

"""Helper functions."""

from flask import current_app
from loc.models import User

import datetime
import jwt

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
    #TODO
    token = ''

    return token

def hash_password(password):
    """Hash the provided password using a specific algorithm.

    Args:
        password (str): Plaintext password.

    Returns:
        Hashed password.
    """
    #TODO
    return password

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
