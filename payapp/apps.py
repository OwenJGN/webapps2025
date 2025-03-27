from django.apps import AppConfig
import os

class PayappConfig(AppConfig):
    """
    Application configuration for the PayApp application.
    Defines the default auto field and sets the application name.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payapp'
    path = os.path.dirname(os.path.abspath(__file__))