import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scripts_base.settings')

app = Celery('scripts_base') # TODO old config

# Using a string here means the worker doesn't have to serialize
# app = Celery('scripts_base', backend='redis', broker='redis://localhost:6379')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()  # TODO old config

# app.autodiscover_tasks()@app.task(bind=True)


@app.task(bind=True)   # TODO old config
def debug_task(self):
    print(f'Request: {self.request!r}')
    print('Request: {0!r}'.format(self.request))


