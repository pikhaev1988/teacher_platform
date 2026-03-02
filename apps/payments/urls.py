from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('tariffs/', views.tariffs, name='tariffs'),
    path('create-payment/', views.create_payment, name='create_payment'),
    path('success/', views.payment_success, name='success'),
    path('failed/', views.payment_failed, name='failed'),
    path('history/', views.transaction_history, name='history'),
    path('webhook/yookassa/', views.yookassa_webhook, name='yookassa_webhook'),
]