from django.core.exceptions import ValidationError


class UppercaseValidator:
    """
    Password validator that ensures passwords contain at least one uppercase letter.
    Used with Django's password validation system.
    """

    def validate(self, password, user=None):
        """
        Validate that the password contains at least one uppercase letter.

        Args:
            password: The password to validate
            user: The user (optional)

        Raises:
            ValidationError: If the password doesn't contain an uppercase letter
        """
        if not any(char.isupper() for char in password):
            raise ValidationError(
                "Password must contain at least one uppercase letter.",
                code='password_no_uppercase',
            )

    def get_help_text(self):
        """
        Return help text for this validator to be displayed to the user.

        Returns:
            str: Help text explaining the requirement
        """
        return "Your password must contain at least one uppercase letter."