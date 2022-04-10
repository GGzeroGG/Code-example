import os

from celery_app import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('bac')
app.config_from_object('config.settings', namespace='CELERY')

app.autodiscover_tasks()
