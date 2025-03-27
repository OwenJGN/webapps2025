from django.core.exceptions import ValidationError


class UppercaseValidator:
    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError(
                "Password must contain at least one uppercase letter.",
                code='password_no_uppercase',
            )

    def get_help_text(self):
        return "Your password must contain at least one uppercase letter."