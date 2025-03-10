from django.apps import AppConfig


class RegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'register'

    def ready(self):
        import register.signals
        # Don't access the database during initialization
        # The admin user will be created through the management command