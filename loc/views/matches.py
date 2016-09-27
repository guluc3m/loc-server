# -*- coding: utf-8 -*-

"""Programming matches."""

from flask import Blueprint, request
from loc import db
from loc.helper import messages as m
from loc.helper.deco import login_required
from loc.helper.util import api_error, api_success, user_from_jwt
from loc.models import Match

import datetime


bp_match = Blueprint('match', __name__)


@bp_match.route('/matches/<slug>')
def match_show(slug):
    """Obtain details of a match.

    The long description of the match is only returned if it has already
    started.
    """
    match = (
        Match
        .query
        .filter_by(slug=slug)
    ).first()

    if not match:
        return api_error(m.MATCH_NOT_FOUND), 404

    # Must check date for long description
    has_started = datetime.datetime.now() >= match.start_date

    return api_success(**match.as_dict(has_started)), 200
