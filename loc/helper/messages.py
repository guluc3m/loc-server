# -*- coding: utf-8 -*-

"""Status messages."""

from flask_babel import lazy_gettext as t


ALREADY_FOLLOWING = t('Already following that user')
CHECK_DATA = t('Check field for errors')
JWT_ERROR = t('Error in JWT coding')
JWT_EXPIRED = t('JWT has expired')
JWT_MISSING = t('Request was missing the "token" attribute')
FIELD_MISSING = t('Field was missing in request')
FOLLOW_OK = t('Now following the user')
INVALID_TOKEN = t('Token was not found or has expired')
NOT_FOLLOWING = t('Not following the user')
RECORD_CREATE_ERROR = t('Error creating record')
RECORD_DELETE_ERROR = t('Error deleting record')
RECORD_UPDATE_ERROR = t('Error updating record')
ROLE_MISSING = t('Missing required role')
UNFOLLOW_OK = t('Unfollowed the user')
USER_EXISTS = t('An user with the specified details already exists')
USER_NOT_FOUND = t('User was not found')
