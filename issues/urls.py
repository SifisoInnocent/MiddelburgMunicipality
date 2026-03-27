from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('report/', views.report_issue, name='report_issue'),
    path('track/', views.track_issue, name='track_issue'),  # New tracking page without reference number
    path('track/<str:reference_number>/', views.track_issue_detail, name='track_issue_detail'),  # Detail view with reference number
    path('update-status/<int:issue_id>/', views.update_issue_status, name='update_issue_status'),
    path('add-feedback/<int:issue_id>/', views.add_feedback, name='add_feedback'),
]