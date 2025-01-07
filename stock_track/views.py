from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import BatchForm


def index(request):
	return render(request, 'stock_track/index.html')


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
    
    if request.method == "POST":
        batch.delete()
        return redirect("stock_track:batch_list")
    
    return render(request, "batch_confirm_delete.html", {"batch": batch})



