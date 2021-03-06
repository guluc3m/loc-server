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

"""Decorator functions."""

from flask import current_app, jsonify, request
from functools import wraps
from werkzeug.exceptions import BadRequest

from loc.helper import util
from loc.helper import messages as m
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
            return util.api_error(m.JWT_MISSING), 500

        if not jwt_token:
            return util.api_fail(token=m.JWT_MISSING), 401

        # Decode
        try:
            decoded = jwt.decode(jwt_token, current_app.config['SECRET_KEY'])

        except jwt.exceptions.DecodeError:
            # TODO log
            return util.api_error(m.JWT_ERROR), 500

        except jwt.ExpiredSignatureError:
            return util.api_error(m.JWT_EXPIRED), 401

        # Get user
        user = User.query.filter_by(
            id=decoded.get('sub', -1),
            is_deleted=False
        ).first()

        if not user:
            return util.api_error(m.USER_NOT_FOUND), 401

        # Token was invalidated?
        if decoded.get('counter', -1) != user._jwt_counter:
            return util.api_error(m.JWT_EXPIRED), 401

        return f(*args, **kwargs)

    return decorated_function

def role_required(role):
    """Require a JWT token and a specific user role to access the decorated view.

    In case the token received is not valid, or hte user does not have the
    required role, the request is aborted with a 401 HTTP status code.

    Args:
        role (str): Name of the required role
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                jwt_token = request.get_json().get('token')

            except BadRequest as e:
                # TODO log except
                return util.api_error(m.JWT_MISSING), 500

            if not jwt_token:
                return util.api_fail(token=m.JWT_MISSING), 401

            # Decode
            try:
                decoded = jwt.decode(jwt_token, current_app.config['SECRET_KEY'])

            except jwt.exceptions.DecodeError:
                # TODO log
                return util.api_error(m.JWT_ERROR), 500

            except jwt.ExpiredSignatureError:
                return util.api_error(m.JWT_EXPIRED), 401

            # Get user
            user = User.query.filter_by(
                id=decoded.get('sub', -1),
                is_deleted=False
            ).first()

            if not user:
                return util.api_error(m.USER_NOT_FOUND), 401

            # Token was invalidated?
            if decoded.get('counter', -1) != user._jwt_counter:
                return util.api_error(m.JWT_EXPIRED), 401

            # Check role
            user_role = (
                UserRole
                .query
                .join(Role, UserRole.role_id==Role.id)
                .filter(UserRole.user_id==user.id)
                .filter(Role.name==role)
            ).first()

            if not user_role:
                return util.api_error(m.ROLE_MISSING), 401

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_required(params):
    """Check that the specified parameters are provided and valid.

    Args:
        params (list[tuple]): List of tuples containing the parameter name
            and the data type that the parameter should be.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            json = request.get_json()

            # Check if JSON was provided
            if not json:
                response = {}
                for p in params:
                    response[p[0]] = m.FIELD_MISSING

                return util.api_fail(**response), 400

            # Check for missing fields and wrong data types
            errors = {}
            for p in params:
                name = p[0]
                p_type = p[1]

                # Missing field
                if name not in json.keys():
                    errors[name] = m.FIELD_MISSING
                    continue

                # Wrong data type
                if not isinstance(json[name], p_type):
                    errors[name] = m.INVALID_TYPE

            # Return errors if any
            if errors:
                return util.api_fail(**errors), 400

            return f(*args, **kwargs)

        return decorated_function

    return decorator

def check_optional(params):
    """Check that the specified parameters are valid.

    This is for optional parameters that may not appear in the request, so
    they will only be checked if present.

    Args:
        params (list[tuple]): List of tuples containing the parameter name
            and the data type that the parameter should be.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            json = request.get_json()

            # Check if JSON was provided
            if not json:
                # Nothing to do
                return f(*args, **kwargs)

            # Check for missing fields and wrong data types
            errors = {}
            for p in params:
                name = p[0]
                p_type = p[1]

                # Missing field, skip it
                if name not in json.keys():
                    continue

                # Wrong data type
                if not isinstance(json[name], p_type):
                    errors[name] = m.INVALID_TYPE

            # Return errors if any
            if errors:
                return util.api_fail(**errors), 400

            return f(*args, **kwargs)

        return decorated_function

    return decorator
