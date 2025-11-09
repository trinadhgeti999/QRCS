from django.apps import AppConfig


class ResponsesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'responses'
    
    def ready(self):
        """Import signals when app is ready."""
        import responses.signals  # noqa


