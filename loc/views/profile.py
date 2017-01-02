# -*- coding: utf-8 -*-

"""Management of user profile."""

from flask import Blueprint, request
from loc import db
from loc.helper import messages as m
from loc.helper.deco import login_required
from loc.helper.util import api_error, api_success, user_from_jwt


bp_profile = Blueprint('profile', __name__)


@bp_profile.route('/profile/followers')
@login_required
def followers():
    """Obtain a list of followers."""
    jwt_token = request.get_json().get('token')
    user = user_from_jwt(jwt_token)

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    response = [f.username for f in user.followers]

    return api_success(followers=response), 200


@bp_profile.route('/profile/following')
@login_required
def following():
    """Obtain a list of users being followed."""
    jwt_token = request.get_json().get('token')
    user = user_from_jwt(jwt_token)

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    response = [f.username for f in user.following]

    return api_success(following=response), 200


@bp_profile.route('/profile')
@login_required
def profile_show():
    """Obtain logged in user's profile.

    This returns the information visible to the user.
    """
    received = request.get_json()
    user = user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    response = {
        'username': user.username,
        'score': user.score
    }

    return api_success(**response), 200


@bp_profile.route('/profile', methods=['PUT'])
@login_required
def profile_update():
    """Update user profile.

    Params:
        name (str)
        email (email)
    """
    received = request.get_json()
    user = user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    # Update information
    name = received.get('name', '')
    email = received.get('email')

    user.name = name
    user.email = email

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        # TODO log
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500

    response = {
        'email': user.email
    }

    return api_success(**response), 200
