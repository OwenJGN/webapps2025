from django.urls import path
from .views import CurrencyConversionView

app_name = 'currency_service'

urlpatterns = [
    # Define the currency conversion endpoint
    # URL format: /currency_service/conversion/{from_currency}/{to_currency}/{amount}/
    path('currency_service/conversion/<str:from_currency>/<str:to_currency>/<str:amount>/',
         CurrencyConversionView.as_view(),
         name='conversion'),
]