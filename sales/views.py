from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Coupon, SaleItem
from .forms import *
from django.forms import inlineformset_factory
from django.db import transaction


@login_required
def manage_coupons(request):
    # Handle form submission for creating a new coupon
    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.company_owner = request.user  # Assign the logged-in user as the owner
            coupon.save()
            messages.success(request, "Coupon created successfully!")
            return redirect("sales:manage_coupons")  # Redirect to the same page after creation
    else:
        form = CouponForm()

    # Fetch all coupons belonging to the logged-in user
    coupons = Coupon.objects.filter(company_owner=request.user)

    return render(request, "sales/manage_coupons.html", {"form": form, "coupons": coupons})


# Update
@login_required
def update_coupon(request, coupon_id):
    
    coupon = get_object_or_404(Coupon, id=coupon_id, company_owner=request.user)
    form = CouponForm(instance=coupon)
    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon updated successfully!")
            return redirect("sales:manage_coupons")
    else:
        form = CouponForm(instance=coupon)
    return render(request, "sales/update_coupon.html", {"form": form})


@login_required
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id, company_owner=request.user)
    coupon.delete()
    messages.success(request, "Coupon deleted successfully!")
    return redirect("sales:manage_coupons")



# Add sale
def add_sale(request):
    SaleItemFormSet = inlineformset_factory(Sale, SaleItem, form=SaleItemForm, extra=1, can_delete=True)

    if request.method == "POST":
        sale_form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST)

        if sale_form.is_valid() and formset.is_valid():
            # Save the sale first
            sale = sale_form.save(commit=False)
            sale.company_owner = request.user
            sale.save()

            # Save the sale items
            sale_items = formset.save(commit=False)
            for item in sale_items:
                item.sale = sale
                item.save()

            # Update the total price of the sale
            sale.update_total_price()

            messages.success(request, "Sale added successfully!")
            return redirect("sales:list")  # Update with the correct URL name for listing sales
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        sale_form = SaleForm()
        formset = SaleItemFormSet()

    context = {
        "sale_form": sale_form,
        "formset": formset,
        "empty_form": formset.empty_form
    }
    return render(request, "sales/add_sale.html", context)


# Display all sales
def sales_list(request):
    
    sales = Sale.objects.filter(company_owner=request.user)
    return render(request, "sales/sales_list.html", {"sales": sales})


# Delete a sale
def delete_sale(request, sale_id):
    
    sale = get_object_or_404(Sale, id=sale_id)
    sale.delete()
    messages.success(request, "The sale was successfully deleted.")
    return redirect("sales:list")


def edit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id, company_owner=request.user)
    SaleItemFormSet = inlineformset_factory(Sale, SaleItem, form=SaleItemForm, extra=1, can_delete=True)

    if request.method == "POST":
        sale_form = SaleForm(request.POST, instance=sale)
        formset = SaleItemFormSet(request.POST, instance=sale)

        if sale_form.is_valid() and formset.is_valid():
            sale = sale_form.save(commit=False)
            sale.company_owner = request.user
            sale.save()

            # Save SaleItems
            sale_items = formset.save(commit=False)
            for item in sale_items:
                item.sale = sale
                item.save()

            sale.update_total_price()
            messages.success(request, "Sale updated successfully!")
            return redirect("sales:list")  # Adjust with your actual URL name

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        sale_form = SaleForm(instance=sale)
        formset = SaleItemFormSet(instance=sale)

    context = {
        "sale_form": sale_form,
        "formset": formset,
        "empty_form": formset.empty_form,
        "sale": sale,
    }
    return render(request, "sales/edit_sale.html", context)

