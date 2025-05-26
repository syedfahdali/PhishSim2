# my_project/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phishsim_fyp.settings')

app = Celery('phishsim_fyp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Example Celery beat schedule (to run tasks periodically)
app.conf.beat_schedule = {
    'send-campaign-emails-every-minute': {
        'task': 'my_app.tasks.send_campaign_emails_task',  # Full path to your task
        'schedule': 60.0,  # Every minute
    },
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
