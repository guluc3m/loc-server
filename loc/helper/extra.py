# -*- coding: utf-8 -*-

"""Extra code used for bootstrapping the application."""

from celery import Celery


def make_celery(app):
    """Create a Celery object for asynchronous tasks.

    Extracted from <http://flask.pocoo.org/docs/0.11/patterns/celery/>

    The application context is needed by extensions such as Flask-Mail.
    """
    celery = Celery(app.import_name, backend=app.config['CELERY_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
