"""
URLs for responses app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResponseTeamViewSet, ResponseLogViewSet

router = DefaultRouter()
router.register(r'teams', ResponseTeamViewSet, basename='response-team')
router.register(r'logs', ResponseLogViewSet, basename='response-log')

urlpatterns = [
    path('', include(router.urls)),
]


