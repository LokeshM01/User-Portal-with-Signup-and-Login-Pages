from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('thank_you/', views.thank_you_view, name='thank_you'),
    path('customers/', views.customer_list_view, name='customer_list'),  # List customers
    path('customers/<int:customer_id>/', views.customer_detail_view, name='customer_detail'),  # View customer details
    path('customers/<int:customer_id>/edit/', views.customer_edit_view, name='customer_edit'),  # Edit customer details
    path('customers/<int:customer_id>/delete/', views.customer_delete_view, name='customer_delete'),  # Delete 
    path('webhook-receiver/', views.webhook_receiver, name='webhook_receiver'),
    path('trigger-webhook/', views.test_webhook_trigger, name='trigger_webhook'),
]
