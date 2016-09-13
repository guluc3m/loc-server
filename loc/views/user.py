# -*- coding: utf-8 -*-

"""Public information of users."""

from flask import Blueprint, request
from loc import db
from loc.helper import messages as m
from loc.helper.deco import login_required
from loc.helper.util import api_error, api_fail, api_success, \
        record_exists, user_from_jwt
from loc.models import Follower, User


bp_user = Blueprint('user', __name__)


@bp_user.route('/users/<username>/follow', methods=['POST'])
@login_required
def follow_user(username):
    """Follow the specified user.

    Args:
        username (str): Unique username.
    """
    jwt_token = request.get_json().get('token')
    user = user_from_jwt(jwt_token)

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    to_follow = (
        User
        .query
        .filter_by(username=username, is_deleted=False)
    ).first()

    if not to_follow:
        return api_fail(username=m.USER_NOT_FOUND), 404

    # Check if already following
    is_following = record_exists(
        Follower,
        follower_id=user.id,
        following_id=to_follow.id
    )

    if is_following:
        return api_fail(username=m.ALREADY_FOLLOWING), 409

    # Create relationship
    new_follow = Follower()
    new_follow.follower_id = user.id
    new_follow.following_id = to_follow.id

    try:
        correct = True
        db.session.add(new_follow)
        db.session.commit()

    except Exception as e:
        #TODO log error
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500

    return api_success(username=m.FOLLOW_OK), 200


@bp_user.route('/users/<username>')
def show_user(username):
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
def show_user_matches(username):
    """Obtain a list of matches in which the user has participated.

    Args:
        username (str): Unique username
    """
    # TODO


@bp_user.route('/users/<username>/unfollow', methods=['POST'])
@login_required
def unfollow_user(username):
    """Unfollow the specified user.

    Args:
        username (str): Unique username.
    """
    jwt_token = request.get_json().get('token')
    user = user_from_jwt(jwt_token)

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    to_unfollow = (
        User
        .query
        .filter_by(username=username, is_deleted=False)
    ).first()

    if not to_unfollow:
        return api_fail(username=m.USER_NOT_FOUND), 404

    # Check if not following
    follow_record = (
        Follower
        .query
        .filter_by(follower_id=user.id, following_id=to_unfollow.id)
    ).first()

    if not follow_record:
        return api_fail(username=m.NOT_FOLLOWING), 409

    try:
        correct = True
        db.session.delete(follow_record)
        db.session.commit()

    except Exception as e:
        #TODO log error
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_DELETE_ERROR), 500

    return api_success(username=m.UNFOLLOW_OK), 200
