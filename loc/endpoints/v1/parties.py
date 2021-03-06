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

"""/v1/parties endpoints."""

from flask import Blueprint, current_app, request
from loc import db
from loc.helper import messages as m, mails, util
from loc.helper.deco import login_required, check_required, check_optional
from loc.helper.util import api_error, api_fail, api_success
from loc.models import Match, MatchParticipant, User, Party
from loc.tasks import async_mail as send_mail

import datetime

v1_parties = Blueprint('v1_parties', __name__)


@v1_parties.route('/join', methods=['POST'])
@login_required
@check_required([('party', str)])
def join_party():
    """Join the specified party.

    Params:
        party (str): Unique party token.
    """
    received = request.get_json()
    party_token = received.get('party')

    # Query party
    party = (
        Party
        .query
        .filter_by(token=party_token)
        .first()
    )

    if not party:
        return api_fail(party=m.PARTY_NOT_FOUND), 404

    # Query match
    match = party.match
    if not match.is_visible or match.is_deleted:
        return api_fail(party=m.PARTY_NOT_FOUND), 404

    if match.start_date < datetime.datetime.utcnow():
        return api_fail(party=m.PARTY_CANNOT_JOIN), 400


    # User record
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404


    # Participant record
    participant = (
        MatchParticipant
        .query
        .filter_by(user_id=user.id, match_id=match.id)
        .first()
    )

    if not participant:
        return api_fail(party=m.NOT_PARTICIPATING), 400

    own_party = participant.party

    # Check if user can join

    # User is in own party with other members
    if own_party and own_party.owner_id == user.id:
        if len(list(own_party.members)) > 1:
            return api_fail(party=m.ALREADY_IN_PARTY), 409

    # User is in another party
    elif own_party:
        return api_fail(party=m.ALREADY_IN_PARTY), 409

    # Destination party is full
    if len(list(party.members)) >= match.max_members:
        return api_fail(party=m.PARTY_FULL), 409


    # Join the party
    own_party.owner_id = None # DIRTY HACK TO ALLOW DELETING THE PARTY
    participant.party_owner_id = party.owner_id

    try:
        correct = True
        db.session.delete(own_party)
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500


    response = {'members': [u.user.username for u in party.members]}
    return api_success(**response), 200


@v1_parties.route('/leave', methods=['POST'])
@login_required
@check_required([('match', str)])
def leave_party():
    """Leave current party for the match

    Params:
        match (str): Unique match slug
    """
    received = request.get_json()
    slug = received.get('match')

    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    if match.start_date < datetime.datetime.utcnow():
        return api_fail(match=m.MATCH_ALREADY_STARTED), 400


    # User record
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404


    # Query participant record
    participant = (
        MatchParticipant
        .query
        .filter_by(match_id=match.id, user_id=user.id)
        .first()
    )

    if not participant:
        return api_fail(match=m.NOT_PARTICIPATING), 404

    if participant.party_owner_id == user.id:
        return api_fail(party=m.PARTY_LEADER), 403

    # Leave the party
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
        db.session.add(new_party)
        participant.party_owner_id = user.id
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500


    response = {'party-token': party_token}
    return api_success(**response), 200


@v1_parties.route('/kick', methods=['POST'])
@check_required([('match', str), ('user', str)])
def kick_member():
    """Kick a member from the party.

    Params:
        match (str): Unique slug of the match.
        user (str): Username of the user to kick.
    """
    received = request.get_json()
    slug = received.get('match')
    username = received.get('user')

    # User record
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404


    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    if match.start_date < datetime.datetime.utcnow():
        return api_fail(match=m.MATCH_ALREADY_STARTED), 400

    # Query participant record
    participant = (
        MatchParticipant
        .query
        .filter_by(match_id=match.id, user_id=user.id)
        .first()
    )

    if not participant:
        return api_fail(match=m.NOT_PARTICIPATING), 404

    if participant.party_owner_id != user.id:
        return api_fail(match=m.NOT_LEADER), 403


    # Check user to delete
    if username == user.username:
        return api_fail(user=m.CANNOT_KICK), 403

    to_kick = User._by_username(username)

    if not user:
        return api_fail(user=m.USER_NOT_FOUND), 404

    participant_to_kick = (
        MatchParticipant
        .query
        .filter_by(match_id=match.id, party_owner_id=user.id, user_id=to_kick.id)
        .first()
    )

    if not participant_to_kick:
        return api_fail(user=m.USER_NOT_FOUND), 404


    # Kick user
    party_token = util.generate_token()

    while util.record_exists(Party, token=party_token):
        party_token = util.generate_token()

    new_party = Party(
        owner_id=to_kick.id,
        match_id=match.id,
        token=party_token,
        is_public=False,
        is_participating=False
    )

    try:
        correct = True
        db.session.add(new_party)
        participant_to_kick.party_owner_id = to_kick.id
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500

    response = {'members': [u.user.username for u in participant.party.members]}

    # Send mail to kicked
    send_mail(
        to_kick.email,
        mails.KICKED_SUBJECT,
        mails.KICKED_BODY % {
            'username': to_kick.username,
            'match': match.title
        },
        mails.KICKED_HTML % {
            'username': to_kick.username,
            'match': match.title
        },
    )

    return api_success(**response), 200


@v1_parties.route('/disband', methods=['POST'])
@check_required([('match', str)])
def disband_party():
    """Disband a party.

    Params:
        match (str): Unique slug of the match.
    """
    received = request.get_json()
    slug = received.get('match')

    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    if match.start_date < datetime.datetime.utcnow():
        return api_fail(match=m.MATCH_ALREADY_STARTED), 400


    # User record
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404


    # Query party
    party = (
        Party
        .query
        .filter_by(match_id=match.id, owner_id=user.id)
        .first()
    )

    if not party:
        return api_fail(match=m.NOT_LEADER), 403


    # Kick members
    to_commit = []
    for participant in party.members:
        if participant.user_id == user.id:
            continue

        # Create new party
        party_token = util.generate_token()

        while util.record_exists(Party, token=party_token):
            party_token = util.generate_token()

        new_party = Party(
            owner_id=participant.user_id,
            match_id=match.id,
            token=party_token,
            is_public=False,
            is_participating=False
        )

        to_commit.append((new_party, participant))


    # Change own token
    party.is_public = False
    party_token = util.generate_token()

    while util.record_exists(Party, token=party_token):
        party_token = util.generate_token()

    party.token = party_token


    try:
        correct = True

        # Add parties and update participants
        for c in to_commit:
            db.session.add(c[0])
            c[1].party_owner_id = c[1].user_id

        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500


    response = {'party-token': party_token}
    return api_success(**response), 200


@v1_parties.route('/lfg', methods=['POST'])
@check_required([('match', str), ('lfg', bool)])
def set_lfg():
    """Set LFG visibility.

    Params:
        match (str): Unique slug of the match.
        lfg (bool): Whether the party is looking for members.
    """
    received = request.get_json()
    slug = received.get('match')
    lfg = received.get('lfg')

    # Query match
    match = Match._by_slug(slug)

    if not match:
        return api_fail(match=m.MATCH_NOT_FOUND), 404

    if match.start_date < datetime.datetime.utcnow():
        return api_fail(match=m.MATCH_ALREADY_STARTED), 400


    # User record
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404


    # Query party
    party = (
        Party
        .query
        .filter_by(owner_id=user.id, match_id=match.id)
        .first()
    )

    if not party:
        return api_fail(match=m.NOT_LEADER), 403


    # Set LFG flag
    party.is_public = lfg

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500


    return api_success(lfg=party.is_public), 200


@v1_parties.route('/list')
@login_required
@check_optional([('page', int)])
def user_parties():
    """List parties the logged in user is in.

    Params:
        page (int): Optional. Page number to return.
    """
    received = request.get_json()
    page = received.get('page', 1)

    # User record
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404


    # Query parties
    per_page = current_app.config['MATCHES_PER_PAGE']
    entries = (
        db.session
        .query(MatchParticipant)
        .join(Match)
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
    for entry in entries.items:
        details = {}

        # Match details
        match = entry.match

        details['match'] = {
            'title': match.title,
            'start-date': match.start_date.isoformat(),
            'end-date': match.end_date.isoformat(),
            'slug': match.slug
        }

        # Party details
        party = entry.party

        details['party'] = {
            'leader': party.owner.username,
            'members': [u.user.username for u in party.members],
            'party-token': party.token
        }

        response.append(details)

    return api_success(**util.paginated(page, entries.pages, response)), 200


@v1_parties.route('/list-past')
@login_required
@check_optional([('page', int)])
def user_past_parties():
    """List parties the logged in user has been in.

    Params:
        page (int): Optional. Page number to return.
    """
    received = request.get_json()
    page = received.get('page', 1)

    # User record
    user = util.user_from_jwt(received.get('token'))

    if not user:
        return api_error(m.USER_NOT_FOUND), 404


    # Query parties
    per_page = current_app.config['MATCHES_PER_PAGE']
    entries = (
        db.session
        .query(MatchParticipant)
        .join(Match)
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
    for entry in entries.items:
        details = {}

        # Match details
        match = entry.match

        details['match'] = {
            'title': match.title,
            'start-date': match.start_date.isoformat(),
            'end-date': match.end_date.isoformat(),
            'slug': match.slug
        }

        # Party details
        party = entry.party

        details['party'] = {
            'leader': party.owner.username,
            'members': [u.user.username for u in party.members],
            'party-token': party.token
        }

        response.append(details)

    return api_success(**util.paginated(page, entries.pages, response)), 200
