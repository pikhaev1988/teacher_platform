#apps/generator/urls
from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('create/', views.create_request, name='create'),
    path('status/<int:request_id>/', views.request_status, name='request_status'),
    path('status/<int:request_id>/json/', views.get_status_json, name='status_json'),
    path('history/', views.history, name='history'),
    path('download/docx/<int:request_id>/', views.download_docx, name='download_docx'),
    path('download/pptx/<int:request_id>/', views.download_pptx, name='download_pptx'),
    path('cancel/<int:request_id>/', views.cancel_request, name='cancel'),
    path('api/subjects-by-grade/', views.get_subjects_by_grade, name='subjects_by_grade'),
]