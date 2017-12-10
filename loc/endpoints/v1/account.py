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

"""/v1/account endpoints."""

from email_validator import validate_email, EmailNotValidError
from flask import Blueprint, current_app, request
from sqlalchemy import or_
from loc import db
from loc.helper import messages as m, mails, util
from loc.helper.deco import login_required, check_required, check_optional
from loc.helper.util import api_error, api_fail, api_success
from loc.models import User
from loc.tasks import async_mail as send_mail

import datetime
import jwt

v1_account = Blueprint('v1_account', __name__)


@v1_account.route('/signup', methods=['POST'])
@check_required([('username', str), ('email', str), ('password', str)])
def signup():
    """Create a new user.

    Params:
        username (str): Username for the new user (unique).
        email (str): Email for the new user (unique).
        password (str): Password to use.
    """
    received = request.get_json()
    username = received.get('username')
    email = received.get('email')
    password = received.get('password')

    # Check if user already exists
    user_exists = db.session.query(
        User
        .query
        .filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).exists()
    ).scalar()

    if user_exists:
        return api_error(m.USER_EXISTS), 409


    # Check minimum password length
    if len(password) < 8:
        return api_fail(password=m.PASSWORD_LENGTH), 400


    # Check if email is valid
    try:
        v = validate_email(email, check_deliverability=False)
        email = v['email']

    except EmailNotValidError:
        return api_fail(email=m.EMAIL_NOT_VALID), 400


    # Try to create user
    new_user = User(
        username=username,
        email=email,
        password=util.hash_password(password)
    )

    try:
        correct = True
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500


    # Send welcome email
    send_mail(
        new_user.email,
        mails.WELCOME_SUBJECT,
        mails.WELCOME_BODY % {
            'username': username,
            'link': current_app.config['CLIENT_ROOT'] + '/login'
        },
        mails.WELCOME_HTML % {
            'username': username,
            'link': current_app.config['CLIENT_ROOT'] + '/login'
        }
    )

    return api_success(username), 201


@v1_account.route('/login', methods=['POST'])
@check_required([('username', str), ('password', str)])
@check_optional([('remember-me', bool)])
def login():
    """Perform login using the provided credentials.

    The password must be hashed and checked against the one stored in database.

    Params:
        username (str): Username to use for login.
        password (str): Password to use for login.
        remember-me (bool): Optional. Whether the session should remain active
            or expire.
    """
    received = request.get_json()
    username = received.get('username')
    password = received.get('password')
    remember = received.get('remember-me', False)

    # Check user record
    user = User._by_username(username, False)

    if not user or not util.hash_matches(password, user.password):
        return api_fail(username=m.CHECK_DATA, password=m.CHECK_DATA), 401


    # Create JWT token
    if remember:
        expire = util.generate_expiration_date(years=1)

    else:
        expire = util.generate_expiration_date(days=5)

    encoded = jwt.encode(
        {
            'sub': user.id,
            'iat': datetime.datetime.utcnow(),
            'exp': expire,
            'counter': user._jwt_counter
        },
        current_app.config['SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    ).decode()

    return api_success(jwt=encoded), 200


@v1_account.route('/profile')
@login_required
def get_profile():
    """Obtain the profile of the logged in user."""
    user = util.user_from_jwt(request.get_json().get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    response = {
        'username': user.username,
        'name': user.name,
        'points': user.points
    }

    return api_success(**response), 200


@v1_account.route('/profile', methods=['PUT'])
@login_required
@check_optional([('name', str), ('email', str)])
def update_profile():
    """Update user profile.

    Params:
        name (str): New name to use (may be empty)
        email (email): New email to use
    """
    received = request.get_json()
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    name = received.get('name')
    email = received.get('email')

    # Nothing to update?
    if not name and not email:
        return api_success(), 200

    response = {}

    # Check information
    if name is not None:
        user.name = name
        response['name'] = name

    if email:
        # Check if email is valid
        try:
            v = validate_email(email, check_deliverability=False)
            user.email = v['email']
            response['email'] = v['email']

        except EmailNotValidError:
            return api_fail(email=m.EMAIL_NOT_VALID), 400


    # Update profile
    try:
        correct = True
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500

    return api_success(**response), 200

@v1_account.route('/followers')
@login_required
def followers():
    """Obtain a list of followers."""
    user = util.user_from_jwt(request.get_json().get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    response = [f.username for f in user.followers]

    return api_success(followers=response), 200

@v1_account.route('/following')
@login_required
def following():
    """Obtain a list of users being followed."""
    user = util.user_from_jwt(request.get_json().get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    response = [f.username for f in user.following]

    return api_success(following=response), 200


@v1_account.route('/change-password', methods=['POST'])
@login_required
@check_required([('current-password', str), ('new-password', str)])
def change_password():
    """Update account password.

    This invalidates old JWT tokens.

    Params:
        current-password (str): Currently defined password.
        new-password (str): New password to use.
    """
    received = request.get_json()
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    current_password = received.get('current-password')
    new_password = received.get('new-password')


    # Check current password
    if not util.hash_matches(current_password, user.password):
        return api_error(m.INVALID_PASSWORD), 403

    # Check minimum password length
    if len(new_password) < 8:
        response = {'new-password': m.PASSWORD_LENGTH}
        return api_fail(**response), 400


    # Update password (and invalidate previous JWT tokens)
    user.password = util.hash_password(new_password)
    user._jwt_counter += 1

    try:
        correct = True
        db.session.add(user)
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500

    return api_success(), 200

@v1_account.route('/forgot-password', methods=['POST'])
@check_required([('email', str)])
def forgot_password():
    """Generate and send a token to reset user password.

    This endpoint returns a success even if the email does not exist.

    Params:
        email (str): Email for which the password was forgotten.
    """
    received = request.get_json()
    email = received.get('email')

    # Check user record
    user = User._by_email(email)

    if not user:
        return api_success(), 200


    # Generate token
    token = util.generate_token()

    while util.record_exists(User, password_reset_token=token):
        token = util.generate_token()

    user.password_reset_token = token
    user.token_expiration = util.generate_expiration_date(days=1)

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500


    # Send mail to user
    send_mail(
        user.email,
        mails.FORGOT_PASSWORD_SUBJECT,
        mails.FORGOT_PASSWORD_BODY % {
            'username': user.username,
            'link': current_app.config['CLIENT_FORGOT_PASSWORD_URL'] + '/'+ token
        },
        mails.FORGOT_PASSWORD_HTML % {
            'username': user.username,
            'link': current_app.config['CLIENT_FORGOT_PASSWORD_URL'] + '/'+ token
        },
    )

    return api_success(), 200

@v1_account.route('/reset-password')
@check_required([('token', str)])
def validate_password_token():
    """Validate the token generated in forgot_password().

    Params:
        token (str): Reset password token.
    """
    received = request.get_json()
    reset_token = received.get('token')

    # Check if token is valid
    token_valid = db.session.query(
        User
        .query
        .filter(
            User.password_reset_token==reset_token,
            User.token_expiration>datetime.datetime.utcnow(),
            User.is_deleted==False
        ).exists()
    ).scalar()

    if not token_valid:
        return api_fail(token=m.INVALID_TOKEN), 404

    return api_success(), 200

@v1_account.route('/reset-password', methods=['POST'])
@check_required([('token', str), ('password', str), ('confirm-password', str)])
def reset_password():
    """Reset user password using token generated in forgot_password().

    Params:
        token (str): Reset password token.
        password (str): New password
        confirm-password (str): Password confirmation.
    """
    received = request.get_json()
    token = received.get('token')
    password = received.get('password')
    confirm_password = received.get('confirm-password')

    # Check minimum password length
    if len(password) < 8:
        return api_fail(password=m.PASSWORD_LENGTH), 400


    # Check password confirmation
    if password != confirm_password:
        response = {'confirm-password': m.PASSWORD_NO_MATCH}
        return api_fail(**response), 400


    # Get user record
    user = (
        User
        .query
        .filter(
            User.password_reset_token==token,
            User.token_expiration>datetime.datetime.utcnow(),
            User.is_deleted==False
        )
    ).first()

    if not user:
        return api_fail(token=m.INVALID_TOKEN), 404


    # Update password (and invalidate previous JWT tokens)
    user.password = util.hash_password(password)
    user._jwt_counter += 1
    user.token=None
    user.token_expiration = None

    try:
        correct = True
        db.session.add(user)
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500

    return api_success(), 200
