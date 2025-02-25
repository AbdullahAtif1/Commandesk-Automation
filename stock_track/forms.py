from django import forms
from .models import *
from django.forms import inlineformset_factory

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


class ProductVariationForm(forms.ModelForm):
    class Meta:
        model = ProductVariation
        fields = ['name', 'sku', 'price', 'image']

ProductVariationInlineFormSet = inlineformset_factory(
    Product,
    ProductVariation,
    form=ProductVariationForm,
    extra=1,  # Number of empty forms to display
    can_delete=True  # Allow deletion of variations
)


class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'product_variation', 'batch', 'warehouse', 'quantity']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('company_owner', None)  # Retrieve the user from the view
        super().__init__(*args, **kwargs)

        if user:
            # Filter related fields based on the logged-in user
            self.fields['product'].queryset = Product.objects.filter(company_owner=user)
            self.fields['product_variation'].queryset = ProductVariation.objects.filter(
                product__company_owner=user
            )
            self.fields['batch'].queryset = Batch.objects.filter(company_owner=user)
            self.fields['warehouse'].queryset = Warehouse.objects.filter(company_owner=user)


class InventoryLogForm(forms.ModelForm):
    class Meta:
        model = InventoryLog
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Reason for updating inventory...'}),
        }

