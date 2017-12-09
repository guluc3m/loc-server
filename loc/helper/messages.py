# -*- coding: utf-8 -*-

"""Status messages."""

from flask_babel import lazy_gettext as t



# JWT
JWT_ERROR = t('Error in JWT coding')
JWT_EXPIRED = t('JWT has expired')
JWT_MISSING = t('Request was missing the JWT token')

# Matches
MATCH_EXISTS = t('Match already exists')
MATCH_NOT_FOUND = t('Match was not found')
MATCH_ALREADY_STARTED = t('Match has already started')
MATCH_ALREADY_FINISHED = t('Match has already finished')
MATCH_NOT_STARTED = t('Match has not started')
MATCH_NOT_FINISHED = t('Match not finished')
ALREADY_PARTICIPATING = t('You are already participating in the match')
NOT_PARTICIPATING = t('You are not participating in the match')

# Parameters
CHECK_DATA = t('Check field for errors')
FIELD_MISSING = t('Field was missing in request')

# Party
PARTY_NOT_EMPTY = t('Your party is not empty')
PARTY_NOT_FOUND = t('Could not find party')
NOT_LEADER = t('You are not the leader of the party')

# Record
RECORD_CREATE_ERROR = t('Error creating record')
RECORD_DELETE_ERROR = t('Error deleting record')
RECORD_UPDATE_ERROR = t('Error updating record')
RECORD_NOT_FOUND = t('Record not found')

# User
USER_EXISTS = t('A user with the specified details already exists')
USER_NOT_FOUND = t('User was not found')
ALREADY_FOLLOWING = t('Already following that user')
FOLLOW_OK = t('Now following the user')
NOT_FOLLOWING = t('Not following the user')
ROLE_MISSING = t('Missing required role')
UNFOLLOW_OK = t('Unfollowed the user')
EMAIL_NOT_VALID = t('Email address is not valid')
INVALID_PASSWORD = t('Invalid password')
PASSWORD_LENGTH = t('Password should be at least 8 characters long')
PASSWORD_NO_MATCH = t('Password does not match')


# Other
OP_NOT_PERMITTED = t('Operation not permitted')
INVALID_TOKEN = t('Token was not found or has expired')
PAGE_INVALID = t('Not a valid page number')
