"""
URL configuration for qrcs_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('frontend.urls')),
    path('admin/', admin.site.urls),
]

# Add REST Framework URLs if available
try:
    from rest_framework.routers import DefaultRouter
    from incidents.views import IncidentViewSet, IncidentCategoryViewSet
    from responses.views import ResponseTeamViewSet, ResponseLogViewSet
    from notifications.views import NotificationViewSet
    
    router = DefaultRouter()
    router.register(r'incidents', IncidentViewSet, basename='incident')
    router.register(r'incident-categories', IncidentCategoryViewSet, basename='incident-category')
    router.register(r'response-teams', ResponseTeamViewSet, basename='response-team')
    router.register(r'response-logs', ResponseLogViewSet, basename='response-log')
    router.register(r'notifications', NotificationViewSet, basename='notification')
    
    urlpatterns += [
        path('api/', include(router.urls)),
    ]
    
    # Add JWT authentication if available
    try:
        from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
        urlpatterns += [
            path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        ]
    except ImportError:
        pass
    
    # Add API documentation if available
    try:
        from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
        urlpatterns += [
            path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
            path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        ]
    except ImportError:
        pass
    
    # Add app URLs
    try:
        urlpatterns += [
            path('api/accounts/', include('accounts.urls')),
            path('api/dashboard/', include('dashboard.urls')),
        ]
    except Exception:
        pass
    
except ImportError:
    # REST Framework not installed - skip API URLs
    pass

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

