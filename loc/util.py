# -*- coding: utf-8 -*-

from flask import abort, current_app, request
from functools import wraps
from werkzeug.exceptions import BadRequest
from loc.models import Role, User, UserRole

import jwt

def hash_password(password):
    """Hash the provided password using a specific algorithm.

    Args:
        password (str): Plaintext password

    Returns:
        Hashed password
    """
    #TODO
    return password

def login_required(f):
    """Require a JWT token to access the decorated view.

    In case the token received is not valid, the request is aborted with a
    401 HTTP status code.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            jwt_token = request.get_json().get('token')

        except BadRequest as e:
            return e

        if not jwt_token:
            abort(401)

        # Decode
        try:
            decoded = jwt.decode(jwt_token, current_app.config['SECRET_KEY'])

        except jwt.ExpiredSignatureError:
            #TODO log
            abort(401)

        # Get user
        user = User.query.filter_by(
            id=decoded.get('sub', -1),
            is_deleted=False
        ).first()

        if not user:
            abort(401)

        return f(*args, **kwargs)

    return decorated_function

def role_required(role):
    """Require a JWT token and a specific user role to access the decorated view.

    In case the token received is not valid, or hte user does not have the
    required role, the request is aborted with a 401 HTTP status code.

    Args:
        role (str): Name of the role required
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                jwt_token = request.get_json().get('token')

            except BadRequest as e:
                return e

            if not jwt_token:
                abort(401)

            # Decode
            try:
                decoded = jwt.decode(jwt_token, current_app.config['SECRET_KEY'])

            except jwt.ExpiredSignatureError:
                #TODO log
                abort(401)

            # Get user
            user = User.query.filter_by(
                id=decoded.get('sub', -1),
                is_deleted=False
            ).first()

            if not user:
                abort(401)


            # Check role
            user_role = (
                UserRole
                .query
                .join(Role, UserRole.role_id==Role.id)
                .filter(UserRole.user_id==user.id)
                .filter(Role.name==role)
            ).first()

            if not user_role:
                abort(401)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
