from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class UserRegisterForm(UserCreationForm):
    """
    Form for user registration that extends Django's UserCreationForm.
    Includes email and name fields in addition to the default username and password.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        """Validate that the email is unique in the system."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email


class UserProfileForm(forms.ModelForm):
    """
    Form for creating or updating user profile information.
    Currently only allows selection of currency preference.
    """

    class Meta:
        model = UserProfile
        fields = ['currency']


class AdminRegistrationForm(UserCreationForm):
    """
    Form for admin registration by existing administrators.
    Creates staff users with administrative privileges.
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        """Validate that the email is unique in the system."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        return email

    def save(self, commit=True):
        """Create a staff user with administrative privileges."""
        user = super().save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating existing user information.
    Allows changes to username, email, and name fields.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        """Validate that the email is unique (except for the current user)."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Email is already in use.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile settings.
    Currently only allows changes to currency preference.
    """

    class Meta:
        model = UserProfile
        fields = ['currency']