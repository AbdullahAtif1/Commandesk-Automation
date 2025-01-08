from django import forms
from .models import *

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ["batch_number", "manufacture_date", "expiry_date", "supplier"]
        widgets = {
            "supplier": forms.Select(),
        }
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_details', 'email']


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'address', 'contact_number']
