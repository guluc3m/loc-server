# -*- coding: utf-8 -*-

"""Public information of users."""

from flask import Blueprint, request
from loc import db
from loc.helper import messages as m
from loc.helper.deco import login_required
from loc.helper.util import api_error, api_fail, api_success, \
        record_exists, user_from_jwt
from loc.models import Follower, Match, User


bp_user = Blueprint('user', __name__)


@bp_user.route('/users/<username>/toggle-follow', methods=['POST'])
@login_required
def user_toggle_follow(username):
    """Toggle following an user.

    Args:
        username (str): Unique username of the user to (un)follow.
    """
    jwt_token = request.get_json().get('token')
    user = user_from_jwt(jwt_token)

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    if user.username == username:
        # Cannot allow user to toggle their own follow record
        return api_error(m.OP_NOT_PERMITTED), 403

    # Check other user exists
    user_toggled = (
        User
        .query
        .filter_by(username=username, is_deleted=False)
    ).first()

    if not user_toggled:
        return api_fail(username=m.USER_NOT_FOUND), 404

    # Create/Delete record
    follow_create = None
    if user_toggled in user.following:
        # Unfollow
        user.following.remove(user_toggled)
        follow_create = False

    else:
        # Follow
        user.following.append(user_toggled)
        follow_create = True

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        #TODO log error
        correct = False

    finally:
        if not correct:
            db.session.rollback()

            if follow_create:
                # Following
                return api_error(m.RECORD_CREATE_ERROR), 500

            else:
                # Unfollowing
                return api_error(m.RECORD_DELETE_ERROR), 500

    if follow_create:
        # Following
        return api_success(username=m.FOLLOW_OK), 200

    else:
        # Unfollowing
        return api_success(username=m.UNFOLLOW_OK), 200


@bp_user.route('/users/<username>')
def user_show(username):
    """Obtain public info for a specific user.

    Args:
        username (str): Unique username.
    """
    user = (
        User
        .query
        .filter_by(username=username, is_deleted=False)
    ).first()

    if not user:
        return api_fail(username=m.USER_NOT_FOUND), 404

    response = {
        'username': user.username,
        'score': user.score
    }

    return api_success(**response), 200


@bp_user.route('/users/<username>/matches')
def user_matches(username):
    """Obtain a list of matches in which the user has participated.

    Args:
        username (str): Unique username
    """
    user = (
        User
        .query
        .filter_by(username=username, is_deleted=False)
    ).first()

    if not user:
        return api_fail(username=m.USER_NOT_FOUND), 404

    response = []

    # Only complete teams are considered
    for team in user.teams:
        if not team.is_participating:
            continue

        match = Match.query.get(team.match_id)

        response.append({
            'team_id': team.id,
            'match_id': match.id,
            'title': match.title,
            'slug': match.slug
        })

    return api_success(*response), 200
