from django.apps import AppConfig

class RegisterConfig(AppConfig):
    """Configuration for the register application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'register'

    def ready(self):
        """Import signals when the app is ready."""
        import register.signals