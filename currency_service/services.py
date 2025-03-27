from decimal import Decimal


class CurrencyConverter:
    """
    A utility class that handles currency conversion calculations.

    This class provides static methods for currency conversion using
    predefined exchange rates. It supports GBP, USD, and EUR currencies.
    """

    # Hard-coded exchange rates (as of 2025)
    EXCHANGE_RATES = {
        'GBP': {'USD': Decimal('1.29'), 'EUR': Decimal('1.20'), 'GBP': Decimal('1.00')},
        'USD': {'GBP': Decimal('0.78'), 'EUR': Decimal('0.93'), 'USD': Decimal('1.00')},
        'EUR': {'GBP': Decimal('0.83'), 'USD': Decimal('1.08'), 'EUR': Decimal('1.00')},
    }

    SUPPORTED_CURRENCIES = ['GBP', 'USD', 'EUR']

    @classmethod
    def is_valid_currency(cls, currency):
        """
        Check if a currency is supported by the conversion service.

        Args:
            currency (str): Currency code to validate

        Returns:
            bool: True if the currency is supported, False otherwise
        """
        return currency in cls.SUPPORTED_CURRENCIES

    @classmethod
    def convert(cls, from_currency, to_currency, amount):
        """
        Convert an amount from one currency to another.

        Args:
            from_currency (str): Source currency code
            to_currency (str): Target currency code
            amount (Decimal): Amount to convert

        Returns:
            Decimal: Converted amount, or None if conversion is not possible
        """
        if not cls.is_valid_currency(from_currency) or not cls.is_valid_currency(to_currency):
            return None

        # Get conversion rate
        rate = cls.EXCHANGE_RATES[from_currency][to_currency]

        # Calculate converted amount
        converted_amount = amount * rate

        # Round to 2 decimal places
        return round(converted_amount, 2)