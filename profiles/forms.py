from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from .models import *

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["client_type", "name", "email", "phone_number", "address", "notes"]
        widgets = {
            "client_type": forms.Select(),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "profile_picture",
            "company_logo",
            "website",
            "store_location",
            "phone_number",
        ]


class CustomSignupForm(UserCreationForm):
    """
    Signup form for new users with only essential fields for account creation.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']  # Essential fields only
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

