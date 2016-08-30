# -*- coding: utf-8 -*-

"""Management of user sessions."""

from flask import Blueprint, abort, current_app, jsonify, request
from sqlalchemy import or_
from sqlalchemy.sql.expression import exists
from loc.models import User
from loc import db, util

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

    if not username or not password:
        abort(401)

    # Check user record
    hashed_password = util.hash_password(password)

    user = (
        User
        .query
        .filter_by(username=username)
    ).first()

    if not user or user.password != hashed_password:
        abort(401)

    # Create JWT token
    if remember:
        expire = datetime.datetime.utcnow() + datetime.timedelta(years=1)

    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)

    encoded = jwt.encode(
        {
            'sub': user.id,
            'iat': datetime.datetime.utcnow(),
            'exp': expire
        },
        current_app.config['SECRET_KEY'],
        algorithm=current_app.config['JWT_ALGORITHM']
    )

    return jsonify(**encoded)

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

    if not username or not email or not password:
        abort(409)

    # Check user record
    user_exists = (
        User
        .query(or_(
            exists().where(User.username==username),
            exists().where(User.email==email)
        ))

    ).scalar()

    if user_exists:
        abort(409)

    # Create user
    new_user = User()
    new_user.username = username
    new_user.email = email
    new_user.password = util.hash_password(password)

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

    response = {}

    return jsonify(**response), 201
