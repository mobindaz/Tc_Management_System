from django.urls import path
from collegeusers import views

urlpatterns = [
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('tutor/dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('ncc/dashboard/', views.ncc_dashboard, name='ncc_dashboard'),
    path('nss/dashboard/', views.nss_dashboard, name='nss_dashboard'),
    path('tc/<int:application_id>/<str:action>/', views.handle_tc_application, name='handle_tc_application'),
    path('approved-list/<str:role>/', views.approved_list_view, name='approved_list'),
    path('pending-applications/<str:role>/', views.pending_applications, name='pending_applications'),
    path('due-list/', views.due_list, name='due_list'),
    path('upload-due-list/', views.upload_due_list, name='upload_due_list'),
    path('tc/<int:tc_id>/approve/', views.approve_tc, name='approve_tc'),
    path('reject/<int:tc_id>/', views.reject_tc, name='reject_tc'),
    path('mark-as-due/<int:tc_id>/', views.mark_as_due, name='mark_as_due'),
    path('approve-due/<int:application_id>/', views.approve_due_application, name='approve_due_application'),
    path('reject-due/<int:application_id>/', views.reject_due_application, name='reject_due_application'),
]