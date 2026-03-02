from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем модуль настроек Django по умолчанию для программы 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('teacher_platform')

# Используем строку конфигурации из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загружаем задачи из всех зарегистрированных приложений Django
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')