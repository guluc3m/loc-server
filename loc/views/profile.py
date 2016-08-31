# -*- coding: utf-8 -*-

"""Management of user profile."""

from flask import Blueprint, abort, request
from loc import db, util
from loc import messages as msg
from loc.deco import login_required
from loc.models import User


bp_profile = Blueprint('profile', __name__)


@bp_profile.route('/profile')
@login_required
def show_profile():
    """Show currently logged in user's profile."""
    jwt_token = request.get_json().get('token')
    user = util.user_from_jwt(jwt_token)

    if not user:
        return util.api_error(msg.USER_NOT_FOUND), 404

    response = {
        'username': user.username,
        'name': user.name,
        'score': user.score
    }

    return util.api_success(**response), 200

@bp_profile.route('/profile/edit', methods=['GET','POST'])
@login_required
def update_profile():
    """Update user profile.

    When a GET request is received, returns current fields (and their values)
    that can be edited.

    After update (POST request), returns updated information.
    """
    received = request.get_json()
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return util.api_error(msg.USER_NOT_FOUND), 404

    if request.method == 'GET':
        # Get information that can be edited
        response = {
            'name': user.name,
            'email': user.email
        }

        return util.api_success(**response), 200

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
            abort(500)

    response = {
        'name': user.name,
        'email': user.email
    }

    return util.api_success(**response), 200
