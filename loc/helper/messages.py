# -*- coding: utf-8 -*-

"""Status messages."""

from flask_babel import lazy_gettext as t



# JWT
JWT_ERROR = t('Error in JWT coding')
JWT_EXPIRED = t('JWT has expired')
JWT_MISSING = t('Request was missing the "token" attribute')

# Matches
MATCH_EXISTS = t('Match already exists')
MATCH_NOT_FOUND = t('Match was not found')

# Parameters
CHECK_DATA = t('Check field for errors')
FIELD_MISSING = t('Field was missing in request')

# Record
RECORD_CREATE_ERROR = t('Error creating record')
RECORD_DELETE_ERROR = t('Error deleting record')
RECORD_UPDATE_ERROR = t('Error updating record')

# User
USER_EXISTS = t('An user with the specified details already exists')
USER_NOT_FOUND = t('User was not found')
ALREADY_FOLLOWING = t('Already following that user')
FOLLOW_OK = t('Now following the user')
NOT_FOLLOWING = t('Not following the user')
ROLE_MISSING = t('Missing required role')
UNFOLLOW_OK = t('Unfollowed the user')


# Other
OP_NOT_PERMITTED = t('Operation not permitted')
INVALID_TOKEN = t('Token was not found or has expired')
