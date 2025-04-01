from django.apps import AppConfig

class CurrencyServiceConfig(AppConfig):
    """
    Configuration class for the Currency Service application.
    This app provides currency conversion functionality as a RESTful service.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'currency_service'