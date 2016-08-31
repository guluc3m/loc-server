# -*- coding: utf-8 -*-

"""Status messages."""

CHECK_DATA = 'CHECK_DATA' # The indicated field must be checked for errors
JWT_EXPIRED = 'JWT_EXPIRED'
JWT_MISSING = 'JWT_MISSING' # 'token' attribute is missing
FIELD_MISSING = 'FIELD_MISSING' # Missing field in request
INVALID_TOKEN = 'INVALID_TOKEN' # Token is not found or has expired
ROLE_MISSING = 'ROLE_MISSING' # User does not have required role
USER_EXISTS = 'USER_EXISTS' # An user with specified details already exists
USER_NOT_FOUND = 'USER_NOT_FOUND'
