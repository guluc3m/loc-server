SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test.db"
SECRET_KEY = "potato"
DEBUG = True

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
