# -*- coding: utf-8 -*-

"""Decorator functions."""

from flask import abort, current_app, jsonify, request
from functools import wraps
from werkzeug.exceptions import BadRequest
from loc import messages as msg
from loc import util
from loc.models import Role, User, UserRole

import jwt

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
            # TODO log except
            abort(500)

        if not jwt_token:
            return util.api_fail(token=msg.JWT_MISSING), 401

        # Decode
        try:
            decoded = jwt.decode(jwt_token, current_app.config['SECRET_KEY'])

        except jwt.ExpiredSignatureError:
            #TODO log
            return util.api_error(msg.JWT_EXPIRED), 401

        # Get user
        user = User.query.filter_by(
            id=decoded.get('sub', -1),
            is_deleted=False
        ).first()

        if not user:
            return util.api_error(msg.USER_NOT_FOUND), 401

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
                # TODO log except
                abort(500)

            if not jwt_token:
                return util.api_fail(token=msg.JWT_MISSING), 401

            # Decode
            try:
                decoded = jwt.decode(jwt_token, current_app.config['SECRET_KEY'])

            except jwt.ExpiredSignatureError:
                #TODO log
                return util.api_error(msg.JWT_EXPIRED), 401

            # Get user
            user = User.query.filter_by(
                id=decoded.get('sub', -1),
                is_deleted=False
            ).first()

            if not user:
                return util.api_error(msg.USER_NOT_FOUND), 401

            # Check role
            user_role = (
                UserRole
                .query
                .join(Role, UserRole.role_id==Role.id)
                .filter(UserRole.user_id==user.id)
                .filter(Role.name==role)
            ).first()

            if not user_role:
                return util.api_error(msg.ROLE_MISSING), 401

            return f(*args, **kwargs)

        return decorated_function

    return decorator
