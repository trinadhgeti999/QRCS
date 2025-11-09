"""
URLs for incidents app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncidentViewSet, IncidentCategoryViewSet

router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')
router.register(r'categories', IncidentCategoryViewSet, basename='incident-category')

urlpatterns = [
    path('', include(router.urls)),
]


