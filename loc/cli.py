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

"""Custom server commands."""

import datetime
import click
from loc import app, db
from loc.helper import util
from loc.models import *


@app.cli.command()
def dbseed():
    """Populate the database with sample data."""
    # Users
    for i in range(1, 15):
        db.session.add(User(
            username='testuser%d' % i,
            email='testuser%d@test.com' % i,
            password = util.hash_password('12345678')
        ))

    db.session.commit()

    # Matches
    db.session.add(Match(
        title='Test match 1',
        short_description='This is a test match',
        long_description='Lorem ipsum',
        start_date=datetime.datetime(
            year=2016,
            month=1,
            day=1,
            hour=0,
            minute=0
        ),
        end_date=datetime.datetime(
            year=2016,
            month=1,
            day=9,
            hour=0,
            minute=0
        ),
        min_members=1,
        max_members=3,
        leaderboard=True,
        slug='test-match-1',
        is_visible=True
    ))
    db.session.add(Match(
        title='Test match 2',
        short_description='This is a test match',
        long_description='Lorem ipsum',
        start_date=datetime.datetime(
            year=2017,
            month=1,
            day=1,
            hour=0,
            minute=0
        ),
        end_date=datetime.datetime(
            year=2026,
            month=1,
            day=9,
            hour=0,
            minute=0
        ),
        min_members=1,
        max_members=3,
        leaderboard=False,
        slug='test-match-2',
        is_visible=True
    ))
    db.session.add(Match(
        title='Test match 3',
        short_description='This is a test match',
        long_description='Lorem ipsum',
        start_date=datetime.datetime(
            year=2026,
            month=1,
            day=1,
            hour=0,
            minute=0
        ),
        end_date=datetime.datetime(
            year=2026,
            month=1,
            day=9,
            hour=0,
            minute=0
        ),
        min_members=1,
        max_members=3,
        leaderboard=False,
        slug='test-match-3',
        is_visible=True
    ))

    db.session.commit()

    # Match participants
    db.session.add(MatchParticipant(user_id=1, match_id=1, party_owner_id=1))
    db.session.add(MatchParticipant(user_id=3, match_id=1, party_owner_id=3))
    db.session.add(MatchParticipant(user_id=4, match_id=1, party_owner_id=3))
    db.session.add(MatchParticipant(user_id=5, match_id=1, party_owner_id=3))
    db.session.add(MatchParticipant(user_id=6, match_id=1, party_owner_id=8))
    db.session.add(MatchParticipant(user_id=7, match_id=1, party_owner_id=7))
    db.session.add(MatchParticipant(user_id=8, match_id=1, party_owner_id=8))
    db.session.add(MatchParticipant(user_id=9, match_id=1, party_owner_id=7))
    db.session.add(MatchParticipant(user_id=10, match_id=1, party_owner_id=10))
    db.session.add(MatchParticipant(user_id=11, match_id=1, party_owner_id=10))
    db.session.add(MatchParticipant(user_id=12, match_id=1, party_owner_id=12))

    db.session.add(MatchParticipant(user_id=1, match_id=2, party_owner_id=1))
    db.session.add(MatchParticipant(user_id=5, match_id=2, party_owner_id=5))
    db.session.add(MatchParticipant(user_id=7, match_id=2, party_owner_id=7))

    db.session.commit()

    # Parties
    db.session.add(Party(owner_id=1, match_id=1, token=util.generate_token(), is_public=False, is_participating=True, position=1))
    db.session.add(Party(owner_id=3, match_id=1, token=util.generate_token(), is_public=False, is_participating=True, position=6))
    db.session.add(Party(owner_id=8, match_id=1, token=util.generate_token(), is_public=False, is_participating=True, position=2))
    db.session.add(Party(owner_id=7, match_id=1, token=util.generate_token(), is_public=False, is_participating=True, position=4))
    db.session.add(Party(owner_id=10, match_id=1, token=util.generate_token(), is_public=False, is_participating=True, position=3))
    db.session.add(Party(owner_id=12, match_id=1, token=util.generate_token(), is_public=False, is_participating=True, position=5))

    db.session.add(Party(owner_id=1, match_id=2, token=util.generate_token(), is_public=False, is_participating=True))
    db.session.add(Party(owner_id=5, match_id=2, token=util.generate_token(), is_public=False, is_participating=True))
    db.session.add(Party(owner_id=7, match_id=2, token=util.generate_token(), is_public=False, is_participating=True))

    db.session.commit()

    # Submissions
    db.session.add(Submission(party_owner_id=1, match_id=1, title='', description='', url=''))
    db.session.add(Submission(party_owner_id=3, match_id=1, title='', description='', url=''))
    db.session.add(Submission(party_owner_id=8, match_id=1, title='', description='', url=''))
    db.session.add(Submission(party_owner_id=7, match_id=1, title='', description='', url=''))
    db.session.add(Submission(party_owner_id=10, match_id=1, title='', description='', url=''))
    db.session.add(Submission(party_owner_id=12, match_id=1, title='', description='', url=''))
    db.session.add(Submission(party_owner_id=1, match_id=2, title='', description='', url=''))
    db.session.add(Submission(party_owner_id=5, match_id=2, title='', description='', url=''))
    db.session.add(Submission(party_owner_id=7, match_id=2, title='', description='', url=''))

    db.session.commit()
