# -*- coding: utf-8 -*-

"""Management of user sessions."""

from flask import Blueprint, abort, current_app, request
from sqlalchemy import or_
from loc import db
from loc.helper import messages as msg
from loc.helper.util import api_error, api_fail, api_success, \
        generate_expiration_date, generate_token, hash_matches, \
        hash_password, record_exists
from loc.models import User

import datetime
import jwt

bp_session = Blueprint('session', __name__)


@bp_session.route('/login', methods=['POST'])
def login():
    """Perform login using the provided credentials.

    The password must be hashed and checked against the one stored in database.

    Params:
        username (str)
        password (str)
        remember_me (bool)

    Returns:
        Status code 200 and a JWT token or status code 401 if credentials
        were not valid.
    """
    received = request.get_json()

    username = received.get('username')
    password = received.get('password')
    remember = received.get('remember_me', False)

    error = {}

    if not username:
        error['username'] = msg.FIELD_MISSING
    if not password:
        error['password'] = msg.FIELD_MISSING

    if error:
        return api_fail(**error), 401

    # Check user record
    user = (
        User
        .query
        .filter_by(username=username)
    ).first()

    if not user or hash_matches(password, user.password):
        return (
            api_fail(username=msg.CHECK_DATA, password=msg.CHECK_DATA),
            401
        )

    # Create JWT token
    if remember:
        expire = generate_expiration_date(years=1)

    else:
        expire = generate_expiration_date(days=1)

    encoded = jwt.encode(
        {
            'sub': user.id,
            'iat': datetime.datetime.utcnow(),
            'rol': list(user.role_names),
            'exp': expire
        },
        current_app.config['SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )

    return api_success(jwt=encoded), 200


@bp_session.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset user password.

    Args:
        token (str)

    Params:
        password (str)
    """
    # Check token is valid
    token_valid = db.session.query(
        User
        .query
        .filter(
            User.password_reset_token==token,
            User.token_expiration>datetime.datetime.utcnow(),
            User.is_deleted==False
        ).exists()
    ).scalar()

    if not token_valid:
        return api_fail(token=msg.INVALID_TOKEN), 404

    # Update password
    received = request.get_json()

    password = received.get('password')

    if not password:
        return api_fail(password=msg.FIELD_MISSING), 404

    # Update user record
    user = (
        User
        .query
        .filter_by(password_reset_token=token)
    ).first()

    if not user:
        return api_fail(email=msg.USER_NOT_FOUND), 404

    user.password = hash_password(password)
    user.password_reset_token = None
    user.token_expiration = None

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        #TODO log error
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            abort(500)

    #TODO send email

    return api_success(), 200


@bp_session.route('/reset-password', methods=['POST'])
def send_reset_token():
    """Generate and send a token to reset user password.

    Params:
        email (str)
    """
    received = request.get_json()

    email = received.get('email')

    if not email:
        return api_fail(email=msg.FIELD_MISSING), 404

    # Check user record
    user = (
        User
        .query
        .filter_by(email=email)
    ).first()

    if not user:
        return api_fail(email=msg.USER_NOT_FOUND), 404

    # Generate token
    token = generate_token()

    while record_exists(User, password_reset_token=token):
        token = generate_token()

    user.password_reset_token = token
    user.token_expiration = generate_expiration_date(days=1)

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        #TODO log error
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            abort(500)

    #TODO send email

    return api_success(), 200


@bp_session.route('/signup', methods=['POST'])
def signup():
    """Create a new user record.

    Params:
        username (str)
        email (str)
        password (str)

    Returns:
        Status code 200 and a JWT token or status code 401 if credentials
        were not valid.
    """
    received = request.get_json()

    username = received.get('username')
    email = received.get('email')
    password = received.get('password')

    error = {}

    if not username:
        error['username'] = msg.FIELD_MISSING
    if not email:
        error['email'] = msg.FIELD_MISSING
    if not password:
        error['password'] = msg.FIELD_MISSING

    if error:
        #TODO check status code
        return api_fail(**error), 409

    # Check user record
    user_exists = db.session.query(
        User
        .query
        .filter(
            or_(
                User.username==username,
                User.email==email
            )
        ).exists()
    ).scalar()

    if user_exists:
        #TODO check status code
        return api_error(msg.USER_EXISTS), 409

    # Create user
    new_user = User()
    new_user.username = username
    new_user.email = email
    new_user.password = hash_password(password)

    try:
        correct = True
        db.session.add(new_user)
        db.session.commit()

    except Exception as e:
        #TODO log error
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            abort(500)

    return api_success(username=username), 201
