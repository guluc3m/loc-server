# -*- coding: utf-8 -*-

"""Programming matches."""

from flask import Blueprint, request
from loc import db
from loc.helper import messages as m
from loc.helper.deco import login_required, role_required
from loc.helper.util import api_error, api_fail, api_success, user_from_jwt
from loc.models import Match

import datetime
import slugify


bp_match = Blueprint('match', __name__)


@bp_match.route('/matches', methods=['POST'])
@role_required('admin')
def match_create():
    """Create a new match.

    Params:
        title (str)
        short_description (str)
        long_description (str)
        start_date (date)
        end_date (date)
        min_team (int)
        max_team (int)
        slug (str), optional
        is_visible (bool)
    """
    received = request.get_json()

    data = {
        'title': received.get('title'),
        'short_description': received.get('short_description'),
        'long_description': received.get('long_description'),
        'start_date': received.get('start_date'),
        'end_date': received.get('end_date'),
        'min_team': received.get('min_team'),
        'max_team': received.get('max_team'),
        'is_visible': received.get('is_visible'),
    }

    # Check for missing fields
    error = {}

    for field, value in data.items():
        if not value:
            error[field] = m.FIELD_MISSING

    if error:
        #TODO check status code
        return api_fail(**error), 409

    # Check if match already exists
    data['slug'] = received.get(
        'slug',
        slugify.slugify(data['title'], to_lower=True, max_length=255)
    )

    match_exists = db.session.query(
        Match
        .query
        .filter(Match.slug==data['slug'])
        .exists()
    ).scalar()

    if match_exists:
        #TODO check status code
        return api_error(m.MATCH_EXISTS), 409

    # Create match
    new_match = Match(**data)

    try:
        correct = True
        db.session.add(new_match)
        db.session.commit()

    except Exception as e:
        #TODO log error
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_CREATE_ERROR), 500

    return api_success(
        id=new_match.id,
        title=new_match.title,
        start_date=new_match.start_date,
        end_date=new_match.end_date,
        slug=new_match.slug
    ), 201

@bp_match.route('/matches', methods=['GET'])
def match_list():
    """Obtain a list of matches.

    This list includes past and current matches, but does not include invisible
    or deleted ones.
    """
    matches = (
        Match
        .query
        .filter_by(is_visible=True, is_deleted=False)
        .order_by(Match.start_date.desc())
    ).all()

    result = []

    for match in matches:
        result.append({
            'id': match.id,
            'title': match.title,
            'start_date': match.start_date,
            'end_date': match.end_date,
            'slug': match.slug
        })

    return api_success(**result), 200


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
