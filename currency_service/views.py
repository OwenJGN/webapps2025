from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from .services import CurrencyConverter


class CurrencyConversionView(APIView):
    """
    A RESTful API view that handles currency conversion requests.

    Endpoint: /currency_service/conversion/{from_currency}/{to_currency}/{amount}

    Returns the converted amount along with conversion details or appropriate
    error response if the request is invalid.
    """

    def get(self, request, from_currency, to_currency, amount):
        """
        Convert an amount from one currency to another.

        Args:
            request: The HTTP request object
            from_currency (str): Source currency code (e.g., 'GBP', 'USD', 'EUR')
            to_currency (str): Target currency code (e.g., 'GBP', 'USD', 'EUR')
            amount (str): Amount to convert as a string

        Returns:
            Response: JSON response with conversion details or error message
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