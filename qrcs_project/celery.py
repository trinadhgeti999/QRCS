"""
Celery configuration for qrcs_project.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrcs_project.settings')

app = Celery('qrcs_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


