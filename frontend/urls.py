"""
URLs for frontend app.
"""
from django.urls import path
from . import views

app_name = 'frontend'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('incident/<int:incident_id>/', views.incident_detail, name='incident_detail'),
    path('report/', views.report_incident, name='report_incident'),
    path('my-incidents/', views.my_incidents, name='my_incidents'),
    path('notifications/', views.notifications_list, name='notifications'),
    path('incident/<int:incident_id>/update-status/', views.update_incident_status, name='update_status'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Response Teams URLs
    path('teams/', views.team_list, name='team_list'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
]

