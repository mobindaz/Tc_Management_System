from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.clerk_dashboard, name='clerk_dashboard'),
    path('clerk/pending-list/', views.pending_list, name='pending_list'),
    path('approved-list/', views.approved_list_clerk, name='approved_list_clerk'),
    path('rejected-list/', views.rejected_list_clerk, name='rejected_list_clerk'),
    path('due-list/', views.due_list_clerk, name='due_list_clerk'),
]
