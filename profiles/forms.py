from django import forms
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

