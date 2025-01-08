from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *


def index(request):
	return render(request, 'stock_track/index.html')

############################### Batch Processing

# Read/List View
def batch_list(request):
    batches = Batch.objects.filter(company_owner=request.user)  # Only show the logged-in user's batches
    return render(request, "stock_track/batch_list.html", {"batches": batches})


# Create View
def create_batch(request):
    
    form = BatchForm()
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.company_owner = request.user  # Set the owner to the logged-in user
            batch.save()
            return redirect("stock_track:batch_list")
    else:
        form = BatchForm()
    return render(request, "stock_track/batch_form.html", {"form": form})


# Update View
def update_batch(request, id):
    
    batch = get_object_or_404(Batch, id=id)
    form = BatchForm(instance=batch)
    if batch.company_owner != request.user:
        return HttpResponseForbidden("You are not allowed to edit this batch.")
    
    if request.method == "POST":
        form = BatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            return redirect("stock_track:batch_list")
    else:
        form = BatchForm(instance=batch)
    return render(request, "stock_track/batch_form.html", {"form": form})


# Delete View
def delete_batch(request, id):
    batch = get_object_or_404(Batch, id=id)
    if batch.company_owner != request.user:
        return HttpResponseForbidden("You are not allowed to delete this batch.")
    
    batch.delete()
    return redirect("stock_track:batch_list")


############################### Category Processing

# List Categories
def category_list(request):
    
    categories = Category.objects.filter(company_owner=request.user)
    return render(request, 'stock_track/category_list.html', {'categories': categories})

# Create Category
def create_category(request):
    
    form = CategoryForm()
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.company_owner = request.user  # Set the company_owner to the current user
            category.save()
            return redirect('stock_track:category_list')  # Redirect to the category list after creation
    else:
        form = CategoryForm()
    
    return render(request, 'stock_track/category_form.html', {'form': form, 'action': 'Create'})


# Update Category
def update_category(request, id):
    
    category = get_object_or_404(Category, id=id, company_owner=request.user)
    form = CategoryForm(instance=category)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('stock_track:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'stock_track/category_form.html', {'form': form, 'action': 'Update'})


# Delete Category
def delete_category(request, id):
    category = get_object_or_404(Category, id=id, company_owner=request.user)
    
    category.delete()
    return redirect('stock_track:category_list')


############################### Supplier Processing

# List Suppliers
def supplier_list(request):
    
    suppliers = Supplier.objects.filter(company_owner=request.user)
    return render(request, 'stock_track/supplier_list.html', {'suppliers': suppliers})


# Create Supplier
def create_supplier(request):
    
    form = SupplierForm()
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.company_owner = request.user  # Set the company_owner to the current user
            supplier.save()
            return redirect('stock_track:supplier_list')  # Redirect to the supplier list after creation
    else:
        form = SupplierForm()
    
    return render(request, 'stock_track/supplier_form.html', {'form': form, 'action': 'Create'})


# Update Supplier
def update_supplier(request, id):
    
    supplier = get_object_or_404(Supplier, id=id, company_owner=request.user)
    form = SupplierForm(instance=supplier)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('stock_track:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    
    return render(request, 'stock_track/supplier_form.html', {'form': form, 'action': 'Update'})


# Delete Supplier
def delete_supplier(request, id):
    
    supplier = get_object_or_404(Supplier, id=id, company_owner=request.user)
    supplier.delete()
    return redirect('stock_track:supplier_list')


############################### Warehouse Processing

# List Warehouses
def warehouse_list(request):
    warehouses = Warehouse.objects.filter(company_owner=request.user)
    return render(request, 'stock_track/warehouse_list.html', {'warehouses': warehouses})


# Create Warehouse
def create_warehouse(request):
    if request.method == "POST":
        form = WarehouseForm(request.POST)
        if form.is_valid():
            warehouse = form.save(commit=False)
            warehouse.company_owner = request.user  # Set the company_owner to the current user
            warehouse.save()
            return redirect('stock_track:warehouse_list')  # Redirect to the warehouse list after creation
    else:
        form = WarehouseForm()
    
    return render(request, 'stock_track/warehouse_form.html', {'form': form, 'action': 'Create'})


# Update Warehouse
def update_warehouse(request, id):
    
    warehouse = get_object_or_404(Warehouse, id=id, company_owner=request.user)
    form = WarehouseForm(instance=warehouse)
    if request.method == "POST":
        form = WarehouseForm(request.POST, instance=warehouse)
        if form.is_valid():
            form.save()
            return redirect('stock_track:warehouse_list')
    else:
        form = WarehouseForm(instance=warehouse)
    
    return render(request, 'stock_track/warehouse_form.html', {'form': form, 'action': 'Update'})


# Delete Warehouse
def delete_warehouse(request, id):
    warehouse = get_object_or_404(Warehouse, id=id, company_owner=request.user)
    warehouse.delete()
    return redirect('warehouse_list')



############################### Products Processing

# List Products
def product_list(request):
    products = Product.objects.filter(company_owner=request.user)
    return render(request, 'stock_track/product_list.html', {'products': products})


# Create Product
def create_product(request):
    
    form = ProductForm(company_owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.company_owner = request.user  # Set the company_owner
            product.save()
            form.save_m2m()  # Save the many-to-many relationships
            return redirect('stock_track:product_list')
    else:
        form = ProductForm(company_owner=request.user)
    
    return render(request, 'stock_track/product_form.html', {'form': form, 'action': 'Create'})


# Update Product
def update_product(request, id):
    
    product = get_object_or_404(Product, id=id, company_owner=request.user)
    form = ProductForm(user=request.user, instance=product)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('stock_track:product_list')
    else:
        form = ProductForm(user=request.user, instance=product)
    
    return render(request, 'stock_track/product_form.html', {'form': form, 'action': 'Update'})


# Delete Product
def delete_product(request, id):
    
		product = get_object_or_404(Product, id=id, company_owner=request.user)
		product.delete()
		return redirect('stock_track:product_list')


