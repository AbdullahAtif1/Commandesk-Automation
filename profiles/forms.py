from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["client_type", "name", "email", "phone_number", "address", "notes"]
        widgets = {
            "client_type": forms.Select(),
        }
