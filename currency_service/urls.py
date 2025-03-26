from django.urls import path
from .views import CurrencyConversionView

app_name = 'currency_service'

urlpatterns = [
    path('conversion/<str:from_currency>/<str:to_currency>/<str:amount>/',
         CurrencyConversionView.as_view(),
         name='conversion'),
]