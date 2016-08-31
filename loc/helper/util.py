from flask import jsonify, current_app
from loc.models import User

import datetime
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

def api_fail(**kwargs):
    """Generate a failure JSON response.

    This response is based on the JSend specification and should be used when
    the data received is invalid.

    Keyword arguments are included in the 'data' attribute of the response.
    """
    response = {
        'status': 'fail',
        'data': kwargs
    }

    return jsonify(**response)

def api_success(**kwargs):
    """Generate a success JSON response.

    This response is based on the JSend specification.

    Keyword arguments are included in the 'data' attribute of the response.
    """
    response = {
        'status': 'success',
        'data': kwargs
    }

    return jsonify(**response)

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
