# -*- coding: utf-8 -*-

"""Status messages."""

ALREADY_FOLLOWING = 'ALREADY_FOLLOWING' # User is already following another user
CHECK_DATA = 'CHECK_DATA' # The indicated field must be checked for errors
JWT_ERROR = 'JWT_ERROR' # Error in the coding of the token
JWT_EXPIRED = 'JWT_EXPIRED'
JWT_MISSING = 'JWT_MISSING' # 'token' attribute is missing
FIELD_MISSING = 'FIELD_MISSING' # Missing field in request
FOLLOW_OK = 'FOLLOW_OK' # User is now following another user
INVALID_TOKEN = 'INVALID_TOKEN' # Token is not found or has expired
NOT_FOLLOWING = 'NOT_FOLLOWING' # User is not following another user
RECORD_CREATE_ERROR = 'RECORD_CREATE_ERROR' # Error creating record
RECORD_DELETE_ERROR = 'RECORD_DELETE_ERROR' # Error deleting record
RECORD_UPDATE_ERROR = 'RECORD_UPDATE_ERROR' # Error updating record
ROLE_MISSING = 'ROLE_MISSING' # User does not have required role
UNFOLLOW_OK = 'UNFOLLOW_OK' # User stopped following another user
USER_EXISTS = 'USER_EXISTS' # An user with specified details already exists
USER_NOT_FOUND = 'USER_NOT_FOUND'
