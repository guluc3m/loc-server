# -*- coding: utf-8 -*-

"""Programming matches."""

from flask import Blueprint, request
from loc import db
from loc.helper import messages as m
from loc.helper.deco import login_required, role_required
from loc.helper.util import api_error, api_fail, api_success, \
        check_missing_fields, record_exists
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
    error = check_missing_fields(data)

    if error:
        #TODO check status code
        return api_fail(**error), 409

    # Check if match already exists
    data['slug'] = received.get(
        'slug',
        slugify.slugify(data['title'], to_lower=True, max_length=128)
    )

    if record_exists(Match, slug=data['slug']):
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


@bp_match.route('/matches')
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

    return api_success(matches=result), 200


@bp_match.route('/matches/<slug>')
def match_show(slug):
    """Obtain details of a match.

    The long description of the match is only returned if it has already
    started.

    Args:
        slug (str): Unique slug of the match
    """
    match = (
        Match
        .query
        .filter_by(slug=slug, is_visible=True, is_deleted=False)
    ).first()

    if not match:
        return api_error(m.MATCH_NOT_FOUND), 404

    # Must check date for long description
    has_started = datetime.datetime.now() >= match.start_date

    return api_success(**match.as_dict(has_started)), 200


@bp_match.route('/matches/<slug>', methods=['PUT'])
@role_required('admin')
def match_update(slug):
    """Modify the details of a match.

    Args:
        slug (str): Unique slug of the match

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

    match = (
        Match
        .query
        .filter_by(slug=slug, is_deleted=False)
    ).first()

    if not match:
        return api_error(m.MATCH_NOT_FOUND), 404

    # Check new title and slug
    title = received.get('title')
    new_slug = received.get('slug')

    if new_slug:
        if record_exists(Match, slug=new_slug):
            #TODO check status code
            return api_error(m.MATCH_EXISTS), 409

    elif title:
        new_slug = slugify.slugify(title, to_lower=True, max_length=128)

        if record_exists(Match, slug=new_slug):
            #TODO check status code
            return api_error(m.MATCH_EXISTS), 409

    # Update fields
    match.title = title or match.title
    match.slug = new_slug or match.slug

    match.short_description = (
        received.get('short_description', match.short_description)
    )
    match.long_description = (
        received.get('long_description', match.long_description)
    )
    match.start_date = received.get('start_date', match.start_date)
    match.end_date = received.get('end_date', match.end_date)
    match.min_team = received.get('min_team', match.min_team)
    match.max_team = received.get('max_team', match.max_team)
    match.is_visible = received.get('is_visible', match.is_visible)

    try:
        correct = True
        db.session.commit()

    except Exception as e:
        # TODO log
        correct = False

    finally:
        if not correct:
            db.session.rollback()
            return api_error(m.RECORD_UPDATE_ERROR), 500

    return api_success(**match.as_dict(True)), 200
