from django import forms
from .models import Coupon, SaleItem, Sale
from profiles.models import Client
from stock_track.models import Product, ProductVariation

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ["code", "discount_percentage", "active", "expiry_date"]
        widgets = {
            "expiry_date": forms.DateInput(),
        }
        

class SaleItemForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(),
        label="Product"
    )
    product_variation = forms.ModelChoiceField(
        queryset=ProductVariation.objects.all(),
        required=False,
        widget=forms.Select(),
        label="Product Variation"
    )

    class Meta:
        model = SaleItem
        fields = ['product', 'product_variation', 'quantity']


class SaleForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        widget=forms.Select(),
        label="Client"
    )
    coupon = forms.ModelChoiceField(
        queryset=Coupon.objects.all(),
        required=False,
        widget=forms.Select(),
        label="Coupon"
    )

    class Meta:
        model = Sale
        fields = ['client', 'coupon']

