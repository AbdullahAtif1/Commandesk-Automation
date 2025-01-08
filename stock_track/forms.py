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


class ProductForm(forms.ModelForm):
    batches = forms.ModelMultipleChoiceField(
        queryset=Batch.objects.none(),  # Placeholder; will filter in __init__
        widget=forms.CheckboxSelectMultiple,
        label="Batches",
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'sku', 'price',
            'is_active', 'stock_alert_threshold', 'batches'
        ]

    def __init__(self, *args, **kwargs):
        company_owner = kwargs.pop('company_owner', None)  # Retrieve user from view
        super().__init__(*args, **kwargs)

        if company_owner:
            # Filter batches by company_owner
            self.fields['batches'].queryset = Batch.objects.filter(company_owner=company_owner)
            # Filter categories by company_owner
            self.fields['category'].queryset = Category.objects.filter(company_owner=company_owner)

