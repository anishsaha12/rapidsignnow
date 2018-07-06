from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from django.conf import settings
from django.apps import apps
import dotenv
# Setting the Default Django settings module
dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','rapidsignnow.settings')

app=Celery('rapidsignnow')
        

# Using a String here means the worker will always find the configuration information
app.config_from_object(settings, namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
