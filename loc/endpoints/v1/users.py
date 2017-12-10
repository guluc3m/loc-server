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

"""/v1/users endpoints."""

from flask import Blueprint, current_app, request
from loc import db
from loc.helper import messages as m, util
from loc.helper.deco import login_required, check_required, check_optional
from loc.helper.util import api_error, api_fail, api_success
from loc.models import Follower, Match, MatchParticipant, User, Party

import datetime

v1_users = Blueprint('v1_users', __name__)


@v1_users.route('/profile')
@check_required([('user', str)])
def user_profile():
    """Obtain the profile of the specified user.

    Params:
        user (str): Username of the user to show.
    """
    username = request.get_json().get('user')

    user = User._by_username(username)

    if not user:
        return api_fail(user=m.USER_NOT_FOUND), 404

    response = {
        'username': user.username,
        'name': user.name,
        'points': user.points
    }

    return api_success(**response), 200


@v1_users.route('/followers')
@check_required([('user', str)])
def user_followers():
    """Obtain the users that follow the specified user.

    Params:
        user (str): Username of the user to show.
    """
    username = request.get_json().get('user')

    user = User._by_username(username)

    if not user:
        return api_fail(user=m.USER_NOT_FOUND), 404

    response = [f.username for f in user.followers]

    return api_success(followers=response), 200


@v1_users.route('/following')
@check_required([('user', str)])
def user_following():
    """Obtain the users followed by the specified user.

    Params:
        user (str): Username of the user to show.
    """
    username = request.get_json().get('user')

    user = User._by_username(username)

    if not user:
        return api_fail(user=m.USER_NOT_FOUND), 404

    response = [f.username for f in user.following]

    return api_success(followers=response), 200


@v1_users.route('/follow', methods=['POST'])
@login_required
@check_required([('user', str), ('follow', bool)])
def toggle_follow():
    """Toggle follow state of a user.

    Params:
        user (str): Username of the user to follow/unfollow.
        follow (bool): Flag indicating whether to follow or not.
    """
    received = request.get_json()
    username = received.get('user')
    follow = received.get('follow')

    # User record
    user = util.user_from_jwt(request.get_json().get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    if username == user.username:
        return api_fail(user=m.CANNOT_FOLLOW_YOURSELF), 409


    # Query user
    f_user = User._by_username(username)

    if not f_user:
        return api_fail(user=m.USER_NOT_FOUND), 404


    # Query follow record
    follower = (
        Follower
        .query
        .filter_by(follower_id=user.id, followee_id=f_user.id)
        .first()
    )


    mark_delete = False
    if follower:
        if follow:
            return api_fail(user=m.ALREADY_FOLLOWING), 409

        # Stop following
        mark_delete = True

    if not follower:
        if not follow:
            return api_fail(user=m.NOT_FOLLOWING), 409

        # Start following
        follower = Follower(
            follower_id=user.id,
            followee_id=f_user.id
        )


    try:
        correct = True

        if mark_delete:
            # Stop following
            db.session.delete(follower)
        else:
            # Start following
            db.session.add(follower)

        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500

    return api_success(), 200


@v1_users.route('/matches')
@check_required([('user', str)])
@check_optional([('page', int)])
def user_matches():
    """List matches the logged in user is in.

    Params:
        user (str): Username to search
        page (int): Optional. Page number to return.
    """
    received = request.get_json()
    username = received.get('user')
    page = received.get('page', 1)

    user = User._by_username(username)

    if not user:
        return api_fail(user=m.USER_NOT_FOUND), 404

    # Query matches
    per_page = current_app.config['MATCHES_PER_PAGE']
    matches = (
        db.session
        .query(Match)
        .join(MatchParticipant)
        .filter(
            MatchParticipant.user_id == user.id,
            Match.end_date > datetime.datetime.utcnow(),
            Match.is_visible == True,
            Match.is_deleted == False
        )
        .order_by(Match.start_date.asc())
        .paginate(page, per_page, error_out=False)
    )

    response = []
    for match in matches.items:
        details = {
            'title': match.title,
            'start-date': match.start_date.isoformat(),
            'end-date': match.end_date.isoformat(),
            'slug': match.slug
        }

        response.append(details)

    return api_success(**util.paginated(page, matches.pages, response)), 200


@v1_users.route('/past-matches')
@check_required([('user', str)])
@check_optional([('page', int)])
def user_past_matches():
    """List matches the logged in user is in.

    Params:
        user (str): Username to search
        page (int): Optional. Page number to return.
    """
    received = request.get_json()
    username = received.get('user')
    page = received.get('page', 1)

    user = User._by_username(username)

    if not user:
        return api_fail(user=m.USER_NOT_FOUND), 404

    # Query matches
    per_page = current_app.config['MATCHES_PER_PAGE']
    matches = (
        db.session
        .query(Match)
        .join(MatchParticipant)
        .filter(
            MatchParticipant.user_id == user.id,
            Match.end_date < datetime.datetime.utcnow(),
            Match.is_visible == True,
            Match.is_deleted == False
        )
        .order_by(Match.start_date.asc())
        .paginate(page, per_page, error_out=False)
    )

    response = []
    for match in matches.items:
        details = {
            'title': match.title,
            'start-date': match.start_date.isoformat(),
            'end-date': match.end_date.isoformat(),
            'slug': match.slug
        }

        response.append(details)

    return api_success(**util.paginated(page, matches.pages, response)), 200
