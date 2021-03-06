SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test.db"
SECRET_KEY = "potato"
DEBUG = True

# Server information
SERVER_DESCRIPTION = "Reference LoC server implementation"

# JWT
JWT_ALGORITHM = "HS512"

# Flask-Mail
MAIL_SERVER = ""
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_DEFAULT_SENDER = ""
MAIL_USERNAME = ""
MAIL_PASSWORD = ""

# Celery
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_BACKEND = "redis://localhost:6379"

# Pagination
MATCHES_PER_PAGE = 20
PARTIES_PER_PAGE = 30
USERS_PER_PAGE = 50

# Client pairing
CLIENT_ROOT = "localhost",
CLIENT_FORGOT_PASSWORD_URL = "localhost/%(token)s"
