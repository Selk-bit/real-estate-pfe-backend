import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'real_estate_project.settings')

app = Celery('real_estate_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = 'redis://redis:6379/0'
app.autodiscover_tasks()
