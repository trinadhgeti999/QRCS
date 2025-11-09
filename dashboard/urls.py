"""
URLs for dashboard app.
"""
from django.urls import path
from .views import DashboardStatsView, IncidentTrendView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('trends/', IncidentTrendView.as_view(), name='incident-trends'),
]


