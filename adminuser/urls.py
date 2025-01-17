from django.urls import path
from . import views

urlpatterns = [
    path('manage-users/', views.manage_users, name='manage_users'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    # path('mark-as-due/<int:application_id>/', views.mark_as_due, name='mark_as_due'),
    # path('due-list/', views.admin_due_list, name='admin_due_list'),
    # path('upload-due-list/', views.upload_due_list, name='upload_due_list'),
    # path('reject-tc/<int:application_id>/', views.reject_tc_action, name='reject_tc_action'),
    # path('approve-tc-list/', views.approve_tc_list, name='approve_tc_list'),
    # path('pending-tc-list/', views.pending_tc_list, name='pending_tc_list'),
    # path('approved-tc-list/', views.approved_tc_list, name='approved_tc_list'),
    # path('approve-tc/<int:application_id>/', views.approve_tc_action, name='approve_tc_action'),
]
