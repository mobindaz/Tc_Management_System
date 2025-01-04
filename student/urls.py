from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_dashboard, name='user_dashboard'),  # Dashboard
    path('success-message/', views.success_message, name='success_message'),  # Success message
    path('status/', views.tc_status, name='tc_status'),  # Check TC status
    path('download-tc/<int:application_id>/', views.download_tc_pdf, name='tc_download'),  # Download TC PDF
    path('settings/', views.settings, name='settings'),
    path('application/status/', views.application_status, name='application_status'),
    
]
