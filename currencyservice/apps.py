from django.apps import AppConfig
import os

class CurrencyserviceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'currencyservice'
    path = os.path.dirname(os.path.abspath(__file__))