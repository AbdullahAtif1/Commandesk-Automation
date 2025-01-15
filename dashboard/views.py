from django.shortcuts import render, get_object_or_404, redirect
from .models import ToDoList, ToDoItem, Complaint
from django.contrib import messages
from .forms import ToDoListForm, ToDoItemInlineForm, ComplaintForm

def index(request):
    # Fetch all to-do lists for the logged-in user
    lists = ToDoList.objects.filter(company_owner=request.user).order_by('-created_at')
    selected_list = None

    # Handle list-level actions for the to do list
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create_list":
            # Create a new list
            list_form = ToDoListForm(request.POST)
            if list_form.is_valid():
                new_list = list_form.save(commit=False)
                new_list.company_owner = request.user
                new_list.save()
                return redirect("dashboard:index")  # Replace with your URL name
        elif action == "edit_list":
            # Edit a list title
            list_id = request.POST.get("list_id")
            selected_list = get_object_or_404(ToDoList, id=list_id, company_owner=request.user)
            list_form = ToDoListForm(request.POST, instance=selected_list)
            if list_form.is_valid():
                list_form.save()
                return redirect("dashboard:index")
        elif action == "delete_list":
            # Delete a list
            list_id = request.POST.get("list_id")
            selected_list = get_object_or_404(ToDoList, id=list_id, company_owner=request.user)
            selected_list.delete()
            return redirect("dashboard:index")
        elif action == "add_item":
            # Add a new item to the list
            list_id = request.POST.get("list_id")
            selected_list = get_object_or_404(ToDoList, id=list_id, company_owner=request.user)
            item_form = ToDoItemInlineForm(request.POST)
            if item_form.is_valid():
                new_item = item_form.save(commit=False)
                new_item.to_do_list = selected_list
                new_item.save()
                return redirect("dashboard:index")
        elif action == "edit_item":
            # Edit an item
            item_id = request.POST.get("item_id")
            item = get_object_or_404(ToDoItem, id=item_id, to_do_list__company_owner=request.user)
            item_form = ToDoItemInlineForm(request.POST, instance=item)
            if item_form.is_valid():
                item_form.save()
                return redirect("dashboard:index")
        elif action == "delete_item":
            # Delete an item
            item_id = request.POST.get("item_id")
            item = get_object_or_404(ToDoItem, id=item_id, to_do_list__company_owner=request.user)
            item.delete()
            return redirect("dashboard:index")

    context = {
        "lists": lists,
        "list_form": ToDoListForm(),
        "item_form": ToDoItemInlineForm(),
    }
    return render(request, "dashboard/index.html", context)


def complaint_list(request):
    complaints = Complaint.objects.filter(company_owner=request.user).order_by('-updated_at')
    form = ComplaintForm()

    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.company_owner = request.user
            complaint.save()
            messages.success(request, "Complaint added successfully!")
            return redirect("dashboard:complaint_list")
        else:
            messages.error(request, "Please correct the errors below.")
    
    return render(request, "dashboard/complaint_list.html", {"complaints": complaints, "form": form})


# Edit Complaint
def edit_complaint(request, id):
    complaint = get_object_or_404(Complaint, id=id, company_owner=request.user)
    if request.method == "POST":
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, "Complaint updated successfully!")
            return redirect("dashboard:complaint_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ComplaintForm(instance=complaint)
    return render(request, "dashboard/edit_complaint.html", {"form": form, "complaint": complaint})

# Delete Complaint
def delete_complaint(request, id):
    complaint = get_object_or_404(Complaint, id=id, company_owner=request.user)
    complaint.delete()
    messages.success(request, "Complaint deleted successfully!")
    return redirect("dashboard:complaint_list")

def complaint_detail(request, id):
    """
    View to display the details of a specific complaint.
    """
    complaint = get_object_or_404(Complaint, id=id, company_owner=request.user)
    return render(request, 'dashboard/complaint_detail.html', {'complaint': complaint})
