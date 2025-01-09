from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from .models import ToDoList, ToDoItem
from .forms import ToDoListForm, ToDoItemInlineForm

def index(request):
    # Fetch all to-do lists for the logged-in user
    lists = ToDoList.objects.filter(company_owner=request.user).order_by('-created_at')
    selected_list = None

    # Handle list-level actions
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
