from django import forms
from .models import Batch

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ["batch_number", "manufacture_date", "expiry_date", "supplier"]
        widgets = {
            "supplier": forms.Select(),
        }

