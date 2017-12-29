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

from flask import Blueprint, current_app, request
from loc import db
from loc.helper import messages as m, util
from loc.helper.deco import login_required, check_required, check_optional
from loc.helper.util import api_error, api_fail, api_success
from loc.models import Match, MatchParticipant, Party, Submission, User

import datetime

v1_matches = Blueprint('v1_matches', __name__)


@v1_matches.route('/list')
@check_optional([('page', int)])
def list_current_matches():
    """Return paginated list of current matches.

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
            Match.is_visible == True,
            Match.is_deleted == False,
            Match.end_date >= datetime.datetime.utcnow()
        )
        .order_by(Match.start_date.asc())
        .paginate(page, per_page, error_out=False)
    )

    response = []

    for match in matches.items:
        item = {
            'title': match.title,
            'start-date': match.start_date.isoformat(),
            'end-date': match.end_date.isoformat(),
            'slug': match.slug
        }

        response.append(item)

    return api_success(**util.paginated(page, matches.pages, response)), 200


@v1_matches.route('/list-past')
@check_optional([('page', int)])
def list_past_matches():
    """Return paginated list of past matches.

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
            Match.is_visible == True,
            Match.is_deleted == False,
            Match.end_date <= datetime.datetime.utcnow()
        )
        .order_by(Match.start_date.asc())
        .paginate(page, per_page, error_out=False)
    )

    response = []

    for match in matches.items:
        item = {
            'title': match.title,
            'start-date': match.start_date.isoformat(),
            'end-date': match.end_date.isoformat(),
            'slug': match.slug
        }

        response.append(item)

    return api_success(**util.paginated(page, matches.pages, response)), 200


@v1_matches.route('/info')
@check_required([('match', str)])
def match_info():
    """Get details for a given match.

    Params:
        match (str): Unique slug of the match.
    """
    slug = request.get_json().get('match')

    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    response = match.as_dict(match.start_date <= datetime.datetime.utcnow())

    return api_success(**response), 200

@v1_matches.route('/leaderboard')
@check_required([('match', str)])
@check_optional([('page', int)])
def match_leaderboard():
    """Obtain paginated leaderboard of the match.

    Params:
        match (str): Unique slug of the match.
        page (int): Optional. Page number to return.
    """
    received = request.get_json()
    slug = received.get('match')
    page = received.get('page', 1)

    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    # Is leaderboard posted?
    if not match.leaderboard:
        return api_success(**util.paginated(1, 1, [])), 200

    # Query parties
    per_page = current_app.config['PARTIES_PER_PAGE']
    parties = (
        Party
        .query
        .filter_by(match_id=match.id, is_participating=True)
        .order_by(Party.position.asc())
        .paginate(page, per_page, error_out=False)
    )

    response = []

    for party in parties.items:
        party_details = {
            'leader': '',
            'position': party.position,
            'members': []
        }

        members = (
            db.session
            .query(User.id, User.username)
            .join(MatchParticipant, User.id==MatchParticipant.user_id)
            .filter(
                MatchParticipant.party_owner_id == party.owner_id,
                MatchParticipant.match_id == match.id,
                User.is_deleted == False
            )
            .all()
        )

        for member in members:
            if member[0] == party.owner_id:
                party_details['leader'] = member[1]

            party_details['members'].append(member[1])

        response.append(party_details)


    return api_success(util.paginated(page, parties.pages, response)), 200


@v1_matches.route('/join', methods=['POST'])
@login_required
@check_required([('match', str)])
def join_match():
    """Join the specified match.

    Params:
        match (str): Slug of the match to join
    """
    received = request.get_json()
    slug = received.get('match')

    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404


    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    if match.start_date < datetime.datetime.utcnow():
        return api_fail(match=m.MATCH_ALREADY_STARTED), 403


    # Check if the user is participating
    is_participating = db.session.query(
        MatchParticipant
        .query
        .filter(
            MatchParticipant.user_id == user.id,
            MatchParticipant.match_id == match.id
        ).exists()
    ).scalar()

    if is_participating:
        return api_fail(match=m.ALREADY_PARTICIPATING), 409


    # Create Participant record
    new_participant = MatchParticipant(
        user_id=user.id,
        match_id=match.id,
        party_owner_id=user.id,
    )

    # Create Party token
    party_token = util.generate_token()

    while util.record_exists(Party, token=party_token):
        party_token = util.generate_token()

    new_party = Party(
        owner_id=user.id,
        match_id=match.id,
        token=party_token,
        is_public=False,
        is_participating=False
    )

    try:
        correct = True
        db.session.add(new_participant)
        db.session.add(new_party)
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500


    response = {'party-token': party_token}
    return api_success(**response), 200

@v1_matches.route('/leave', methods=['POST'])
@login_required
@check_required([('match', str)])
def leave_match():
    """Leave the specified match.

    Params:
        match (str): Slug of the match to join
    """
    received = request.get_json()
    slug = received.get('match')

    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404


    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    if match.start_date < datetime.datetime.utcnow():
        return api_fail(match=m.MATCH_ALREADY_STARTED), 403


    # Check if the user is participating
    participant = (
        MatchParticipant
        .query
        .filter(
            MatchParticipant.user_id == user.id,
            MatchParticipant.match_id == match.id
        )
        .first()
    )

    if not participant:
        return api_fail(match=m.NOT_PARTICIPATING), 409


    # Check if party is empty and get token if the user is the leader
    if participant.party_owner_id == user.id:
        other_member = db.session.query(
            MatchParticipant
            .query
            .filter(
                MatchParticipant.user_id != user.id,
                MatchParticipant.match_id == match.id
            ).exists()
        ).scalar()

        if other_member:
            return api_fail(match=m.PARTY_NOT_EMPTY), 403

        party_token = (
            Party
            .query
            .filter_by(owner_id=user.id, match_id=match.id)
            .first()
        )

    try:
        correct = True
        if participant.party_owner_id == user.id:
            db.session.delete(party_token)

        db.session.delete(participant)
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500


    return api_success(), 200


@v1_matches.route('/participants')
@check_required([('match', str)])
@check_optional([('page', int)])
def list_parties():
    """List participating parties.

    Only accessible if the match has started.

    Params:
        match (str): Unique slug of the match.
        page (int): Page number to return.
    """
    received = request.get_json()
    slug = received.get('match')
    page = received.get('page', 1)

    response = []

    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    if match.start_date > datetime.datetime.utcnow():
        return api_success(**util.paginated(1, 1, [])), 200


    # Query parties
    per_page = current_app.config['MATCHES_PER_PAGE']

    parties = (
        Party
        .query
        .filter_by(match_id=match.id, is_participating=True)
        .paginate(page, per_page, error_out=False)
    )

    for party in parties.items:
        party_details = {
            'leader': '',
            'members': []
        }

        members = (
            db.session
            .query(User.id, User.username)
            .join(MatchParticipant, User.id==MatchParticipant.user_id)
            .filter(
                MatchParticipant.party_owner_id == party.owner_id,
                MatchParticipant.match_id == match.id,
                User.is_deleted == False
            )
            .all()
        )

        for member in members:
            if member[0] == party.owner_id:
                party_details['leader'] = member[1]

            party_details['members'].append(member[1])

        response.append(party_details)


    return api_success(**util.paginated(page, parties.pages, response)), 200

@v1_matches.route('/lfg')
@check_required([('match', str)])
@check_optional([('page', int)])
def list_lfg():
    """List parties looking for more members.

    Params:
        match (str): Unique slug of the match.
        page (int): Page number to return.
    """
    received = request.get_json()
    slug = received.get('match')
    page = received.get('page', 1)

    response = []

    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404


    # Query parties
    per_page = current_app.config['MATCHES_PER_PAGE']

    parties = (
        Party
        .query
        .filter_by(match_id=match.id, is_public=True)
        .paginate(page, per_page, error_out=False)
    )

    for party in parties.items:
        party_details = {
            'leader': '',
            'party-token': party.token,
            'members': []
        }

        members = (
            db.session
            .query(User.id, User.username)
            .join(MatchParticipant, User.id==MatchParticipant.user_id)
            .filter(
                MatchParticipant.party_owner_id == party.owner_id,
                MatchParticipant.match_id == match.id,
                User.is_deleted == False
            )
            .all()
        )

        for member in members:
            if member[0] == party.owner_id:
                party_details['leader'] = member[1]

            party_details['members'].append(member[1])

        response.append(party_details)


    return api_success(**util.paginated(page, parties.pages, response)), 200


@v1_matches.route('/submission')
@check_required([('match', str)])
@check_optional([('party', str)])
def show_submission():
    """Obtain details of the party's submission for the given match.

    Params:
        match (str): Unique slug of the match.
        party (str): Optional. Username of the party leader.
    """
    received = request.get_json()
    token = received.get('token')
    slug = received.get('match')
    party_owner = received.get('party')

    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    now = datetime.datetime.utcnow()

    if token and not party_owner:
        # Trying to see own submission
        if now < match.start_date:
            return api_fail(match=m.MATCH_NOT_STARTED), 403

        result = login_required(_show_submission_own)

    elif party_owner:
        # Trying to see other submission (public)
        if now < match.end_date:
            return api_fail(match=m.MATCH_NOT_FINISHED), 403

        result = _show_submission_public

    else:
        return api_fail(party=m.FIELD_MISSING), 400

    return result(match)

def _show_submission_own(match):
    """Show own submission."""
    received = request.get_json()
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    participant = (
        MatchParticipant
        .query
        .filter_by(match_id=match.id, user_id=user.id)
        .first()
    )

    if not participant:
        return api_fail(match=m.NOT_PARTICIPATING), 404

    submission = (
        Submission
        .query
        .filter_by(match_id=match.id, party_owner_id=participant.party_owner_id)
        .first()
    )

    if not submission:
        return api_error(m.RECORD_NOT_FOUND), 500

    response = {
        'title': submission.title,
        'description': submission.description,
        'url': submission.url
    }

    return api_success(**response), 200

def _show_submission_public(match):
    """Show submission of other party."""
    received = request.get_json()
    party_owner = received.get('party')

    user = User._by_username(party_owner)

    if not user:
        return api_fail(party=m.PARTY_NOT_FOUND), 404

    submission = (
        db.session
        .query(Submission)
        .join(Party, Submission.party_owner_id==Party.owner_id)
        .filter(
            Party.owner_id == user.id,
            Party.match_id == match.id,
            User.is_deleted == False
        )
        .first()
    )

    if not submission:
        return api_fail(party=m.PARTY_NOT_FOUND), 404

    response = {
        'title': submission.title,
        'description': submission.description,
        'url': submission.url
    }

    return api_success(**response), 200


@v1_matches.route('/submission', methods=['PUT'])
@login_required
@check_required([('match', str)])
@check_optional([('title', str), ('description', str), ('url', str)])
def edit_submission():
    """Edit a submission.

    Can only be performed by the party leader.

    Params:
        match (str): Unique match slug.
        title (str): New title for the submission.
        description (str): New description for the submission.
        url (str): New URL for the submission.
    """
    received = request.get_json()
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404

    slug = received.get('match')


    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    if match.end_date < datetime.datetime.utcnow():
        return api_fail(match=m.MATCH_ALREADY_FINISHED), 403

    # Query submission
    submission = (
        Submission
        .query
        .filter_by(match_id=match.id, party_owner_id=user.id)
        .first()
    )

    if not submission:
        # Not party leader
        return api_fail(match=m.NOT_LEADER), 403

    # Try to update submission
    submission.title = received.get('title') or submission.title
    submission.description = received.get('description') or submission.description
    submission.url = received.get('url') or submission.url

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500

    response = {
        'title': submission.title,
        'description': submission.description,
        'url': submission.url
    }
    return api_success(**response), 200
