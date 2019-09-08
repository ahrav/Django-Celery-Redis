import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_parroter.settings')

app = Celery('image_parroter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
