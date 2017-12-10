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

"""/v1/admin endpoints."""

from flask import Blueprint, current_app, request
from loc import db
from loc.helper import messages as m, util
from loc.helper.deco import role_required, check_required, check_optional
from loc.helper.util import api_error, api_fail, api_success
from loc.models import Follower, Match, MatchParticipant, User, Party

import datetime
import slugify

v1_admin = Blueprint('v1_admin', __name__)


@v1_admin.route('/match', methods=['POST'])
@role_required('admin')
@check_required([
    ('title', str),
    ('short-description', str),
    ('long-description', str),
    ('start-date', str),
    ('end-date', str),
    ('min-members', int),
    ('max-members', int),
    ('is-visible', bool)
])
@check_optional([('slug', str)])
def new_match():
    """Creates a new match.

    Params:
        title (str): Match title (slug created automatically).
        short-description (str): Short description of the match.
        long-description (str): Long description of the match.
        start-date (datetime): When the match starts.
        end-date (datetime): When the match ends.
        min-members (int): Minimum party members required.
        max-members (int): Maximum party members allowed.
        is-visible (bool): Whether the match can be found.
        slug (str): Optional slug.
    """
    received = request.get_json()
    data = {
        'title': received.get('title'),
        'short_description': received.get('short-description'),
        'long_description': received.get('long-description'),
        'start_date': received.get('start-date'),
        'end_date': received.get('end-date'),
        'min_members': received.get('min-members'),
        'max_members': received.get('max-members'),
        'is_visible': received.get('is-visible'),
        'slug': received.get('slug')
    }

    # Check some data
    errors = {}
    if data['min_members'] <= 0:
        errors['min-members'] = m.INVALID_VALUE

    if data['max_members'] < data['min_members']:
        errors['max-members'] = m.INVALID_VALUE


    try:
        data['start_date'] = datetime.datetime.strptime(
            data['start_date'],
            '%Y-%m-%d %H:%M:%S'
        )

    except ValueError:
        errors['start-date'] = m.INVALID_VALUE

    try:
        data['end_date'] = datetime.datetime.strptime(
            data['end_date'],
            '%Y-%m-%d %H:%M:%S'
        )

    except ValueError as e:
        errors['end-date'] = m.INVALID_VALUE


    if errors:
        return api_fail(**errors), 400


    # Check slug
    if not data['slug']:
        data['slug'] = slugify.slugify(data['title'], to_lower=True)

    if util.record_exists(Match, slug=data['slug']):
        return api_fail(slug=m.SLUG_EXISTS % {'slug': data['slug']}), 409


    # Create match
    new_match = Match(**data)

    try:
        correct = True
        db.session.add(new_match)
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500

    return api_success(slug=new_match.slug), 201


@v1_admin.route('/match', methods=['PUT'])
@role_required('admin')
@check_required([('match', str)])
@check_optional([
    ('title', str),
    ('short-description', str),
    ('long-description', str),
    ('start-date', str),
    ('end-date', str),
    ('min-members', int),
    ('max-members', int),
    ('is-visible', bool),
    ('slug', str)
])
def modify_match():
    """Modify a match.

    Params:
        match (str): Slug of the match to edit
        title (str): Match title (slug created automatically).
        short-description (str): Short description of the match.
        long-description (str): Long description of the match.
        start-date (datetime): When the match starts.
        end-date (datetime): When the match ends.
        min-members (int): Minimum party members required.
        max-members (int): Maximum party members allowed.
        is-visible (bool): Whether the match can be found.
        slug (str): New slug for the match.
    """
    received = request.get_json()

    # Query match
    match = (
        Match
        .query
        .filter_by(slug=received.get('match'), is_deleted=False)
        .first()
    )

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    # Check some data
    data = {
        'title': received.get('title'),
        'short_description': received.get('short-description'),
        'long_description': received.get('long-description'),
        'start_date': received.get('start-date'),
        'end_date': received.get('end-date'),
        'min_members': received.get('min-members'),
        'max_members': received.get('max-members'),
        'is_visible': received.get('is-visible'),
        'slug': received.get('slug')
    }
    errors = {}
    if data['min_members'] and data['min_members'] <= 0:
        errors['min-members'] = m.INVALID_VALUE

    if data['max_members'] and data['max_members'] <= 0:
        errors['max-members'] = m.INVALID_VALUE


    if data['start_date']:
        try:
            data['start_date'] = datetime.datetime.strptime(
                data['start_date'],
                '%Y-%m-%d %H:%M:%S'
            )

        except ValueError:
            errors['start-date'] = m.INVALID_VALUE

    if data['end_date']:
        try:
            data['end_date'] = datetime.datetime.strptime(
                data['end_date'],
                '%Y-%m-%d %H:%M:%S'
            )

        except ValueError as e:
            errors['end-date'] = m.INVALID_VALUE


    if errors:
        return api_fail(**errors), 400


    # Check slug
    if not data['slug'] and data['title']:
        data['slug'] = slugify.slugify(data['title'], to_lower=True)

    if data['slug'] != match.slug:
        if util.record_exists(Match, slug=data['slug']):
            return api_fail(slug=m.SLUG_EXISTS % {'slug': data['slug']}), 409


    # Edit match
    response = {}
    for attribute in data.keys():
        value = data[attribute]

        if value is not None:
            setattr(match, attribute, value)
            response[attribute] = value

    try:
        correct = True
        if match.min_members > match.max_members:
            db.session.rollback()
            error = {
                'min-members': m.INVALID_VALUE,
                'max-members': m.INVALID_VALUE
            }

            return api_fail(**error), 400

        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500

    return api_success(**response), 200


@v1_admin.route('/match-delete', methods=['PUT'])
@role_required('admin')
@check_required([('match', str), ('delete', bool)])
def toggle_match_delete():
    """Toggle deletion of a match.

    Params:
        match (str): Unique slug of the match.
        delete (bool): Flag indicating whether the match will be deleted.
    """
    received = request.get_json()
    slug = received.get('match')
    do_delete = received.get('delete')

    match = (
        Match
        .query
        .filter_by(slug=slug)
        .first()
    )

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    if match.is_deleted and do_delete:
        return api_fail(match=m.ALREADY_DELETED), 409

    if not match.is_deleted and not do_delete:
        return api_fail(match=m.NOT_DELETED), 409


    # Delete/undelete
    response = {}
    match.is_deleted = do_delete

    if do_delete:
        match.delete_date = datetime.datetime.utcnow()
        response['delete-date'] = match.delete_date

    else:
        match.delete_date = None
        response['match'] = match.slug

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500

    return api_success(**response), 200


@v1_admin.route('/deleted-matches')
@role_required('admin')
@check_optional([('page', int)])
def list_deleted_matches():
    """Return paginated list of deleted matches.

    Params:
        page (int): Optional. Page number to return
    """
    received = request.get_json()
    if received:
        page = received.get('page', 1)
    else:
        page = 1

    # Query matches
    per_page = current_app.config['MATCHES_PER_PAGE']

    matches = (
        Match
        .query
        .filter(
            Match.is_deleted == True,
        )
        .order_by(Match.start_date.asc())
        .paginate(page, per_page, error_out=False)
    )

    response = []

    for match in matches.items:
        item = {
            'title': match.title,
            'delete-date': match.delete_date,
            'slug': match.slug
        }

        response.append(item)

    return api_success(**util.paginated(page, matches.pages, response)), 200


@v1_admin.route('/users')
@role_required('admin')
@check_optional([('page', int)])
def list_users():
    """Return paginated list of active users.

    Params:
        page (int): Optional. Page number to return
    """
    received = request.get_json()
    if received:
        page = received.get('page', 1)
    else:
        page = 1

    # Query matches
    per_page = current_app.config['USERS_PER_PAGE']

    users = (
        User
        .query
        .filter(
            User.is_deleted == False,
        )
        .order_by(User.username.asc())
        .paginate(page, per_page, error_out=False)
    )

    response = [u.username for u in users.items]

    return api_success(**util.paginated(page, users.pages, response)), 200


@v1_admin.route('/deleted-users')
@role_required('admin')
@check_optional([('page', int)])
def list_deleted_users():
    """Return paginated list of deleted/banned users.

    Params:
        page (int): Optional. Page number to return
    """
    received = request.get_json()
    if received:
        page = received.get('page', 1)
    else:
        page = 1

    # Query matches
    per_page = current_app.config['USERS_PER_PAGE']

    users = (
        User
        .query
        .filter(
            User.is_deleted == True,
        )
        .order_by(User.username.asc())
        .paginate(page, per_page, error_out=False)
    )

    response = []
    for user in users.items:
        response.append({
            'username': user.username,
            'delete-date': user.delete_date
        })

    return api_success(**util.paginated(page, users.pages, response)), 200


@v1_admin.route('/user-delete', methods=['PUT'])
@role_required('admin')
@check_required([('user', str), ('delete', bool)])
def toggle_user_delete():
    """Toggle deletion of a user.

    This invalidates all JWT tokens.

    Params:
        user (str): Username of the user to delete.
        delete (bool): Flag indicating whether the match will be deleted.
    """
    received = request.get_json()
    username = received.get('user')
    do_delete = received.get('delete')

    user = (
        User
        .query
        .filter_by(username=username)
        .first()
    )

    if not user:
        return api_fail(userh=m.USER_NOT_FOUND), 404

    if user.is_deleted and do_delete:
        return api_fail(user=m.ALREADY_DELETED), 409

    if not user.is_deleted and not do_delete:
        return api_fail(user=m.NOT_DELETED), 409


    # Delete/undelete
    response = {}
    user.is_deleted = do_delete

    if do_delete:
        user.delete_date = datetime.datetime.utcnow()
        user._jwt_counter += 1
        response['delete-date'] = user.delete_date

    else:
        user.delete_date = None
        response['user'] = user.username

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500

    return api_success(**response), 200
