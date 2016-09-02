# -*- coding: utf-8 -*-

"""Status messages."""

ALREADY_FOLLOWING = 'ALREADY_FOLLOWING' # User is already following another user
CHECK_DATA = 'CHECK_DATA' # The indicated field must be checked for errors
JWT_EXPIRED = 'JWT_EXPIRED'
JWT_MISSING = 'JWT_MISSING' # 'token' attribute is missing
FIELD_MISSING = 'FIELD_MISSING' # Missing field in request
FOLLOW_OK = 'FOLLOW_OK' # User is now following another user
INVALID_TOKEN = 'INVALID_TOKEN' # Token is not found or has expired
NOT_FOLLOWING = 'NOT_FOLLOWING' # User is not following another user
ROLE_MISSING = 'ROLE_MISSING' # User does not have required role
UNFOLLOW_OK = 'UNFOLLOW_OK' # User stopped following another user
USER_EXISTS = 'USER_EXISTS' # An user with specified details already exists
USER_NOT_FOUND = 'USER_NOT_FOUND'
