from django.apps import AppConfig
import os

class PayappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payapp'
    path = os.path.dirname(os.path.abspath(__file__))