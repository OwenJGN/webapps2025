from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal


class CurrencyConversionView(APIView):
    """
    A RESTful API view that handles currency conversion
    Endpoint: /webapps2025/conversion/{from_currency}/{to_currency}/{amount}
    """

    # Hard-coded exchange rates (as of 2023)
    EXCHANGE_RATES = {
        'GBP': {'USD': Decimal('1.25'), 'EUR': Decimal('1.15'), 'GBP': Decimal('1.00')},
        'USD': {'GBP': Decimal('0.80'), 'EUR': Decimal('0.92'), 'USD': Decimal('1.00')},
        'EUR': {'GBP': Decimal('0.87'), 'USD': Decimal('1.09'), 'EUR': Decimal('1.00')},
    }

    SUPPORTED_CURRENCIES = ['GBP', 'USD', 'EUR']

    def get(self, request, from_currency, to_currency, amount):
        """
        Convert an amount from one currency to another
        """
        # Convert currencies to uppercase
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Validate currencies
        if from_currency not in self.SUPPORTED_CURRENCIES:
            return Response(
                {
                    'error': f'Invalid source currency: {from_currency}. Supported currencies are: {", ".join(self.SUPPORTED_CURRENCIES)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if to_currency not in self.SUPPORTED_CURRENCIES:
            return Response(
                {
                    'error': f'Invalid target currency: {to_currency}. Supported currencies are: {", ".join(self.SUPPORTED_CURRENCIES)}'},
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
        rate = self.EXCHANGE_RATES[from_currency][to_currency]
        converted_amount = amount * rate

        # Round to 2 decimal places
        converted_amount = round(converted_amount, 2)

        return Response({
            'from_currency': from_currency,
            'to_currency': to_currency,
            'amount': amount,
            'conversion_rate': float(rate),
            'converted_amount': float(converted_amount)
        })