from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from .services import CurrencyConverter


class CurrencyConversionView(APIView):
    """
    A RESTful API view that handles currency conversion
    Endpoint: /currency_service/conversion/{from_currency}/{to_currency}/{amount}
    """

    def get(self, request, from_currency, to_currency, amount):
        """
        Convert an amount from one currency to another
        """
        # Convert currencies to uppercase
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Validate currencies
        if not CurrencyConverter.is_valid_currency(from_currency):
            return Response(
                {
                    'error': f'Invalid source currency: {from_currency}. Supported currencies are: {", ".join(CurrencyConverter.SUPPORTED_CURRENCIES)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not CurrencyConverter.is_valid_currency(to_currency):
            return Response(
                {
                    'error': f'Invalid target currency: {to_currency}. Supported currencies are: {", ".join(CurrencyConverter.SUPPORTED_CURRENCIES)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate amount
        try:
            amount = Decimal(amount)
            if amount < 0:
                return Response(
                    {'error': 'Amount must be non-negative'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except:
            return Response(
                {'error': 'Invalid amount format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Perform the conversion
        rate = CurrencyConverter.EXCHANGE_RATES[from_currency][to_currency]
        converted_amount = CurrencyConverter.convert(from_currency, to_currency, amount)

        if converted_amount is None:
            return Response(
                {'error': 'Conversion failed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': float(amount),
            'conversion_rate': float(rate),
            'converted_amount': float(converted_amount)
        })