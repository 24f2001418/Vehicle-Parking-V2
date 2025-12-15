import os
from celery import Celery


def make_celery(app):
    broker = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    celery = Celery(app.import_name, broker=broker)
    # copy Flask config keys with CELERY_ prefix if needed
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
