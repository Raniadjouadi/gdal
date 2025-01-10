from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery.schedules import crontab
#from django_celery_beat.models import PeriodicTask

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dash.settings')

app = Celery('dash')
app.conf.enable_utc = False
app.conf.update(timezone = 'Africa/Tunis')
app.conf.beat_schedule = {
    'send-mail-ervy-day-at-19 h 23 mn': {
        'task' : 'tache.tasks.send_mail_fonction',
        'schedule' : crontab(hour=10, minute=17),
        #'args':()
    }
}


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(settings, namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')