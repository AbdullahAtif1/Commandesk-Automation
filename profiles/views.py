from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Client
from .forms import ClientForm

@login_required
def client_management(request):
    clients = Client.objects.filter(company_owner=request.user)
    add_form = ClientForm()
    edit_forms = {client.id: ClientForm(instance=client) for client in clients}  # Pre-render forms for each client

    # Handle form submissions
    if request.method == "POST":
        if "add_client" in request.POST:
            # Adding a new client
            add_form = ClientForm(request.POST)
            if add_form.is_valid():
                client = add_form.save(commit=False)
                client.company_owner = request.user
                client.save()
                messages.success(request, "Client added successfully.")
                return redirect("profiles:client_management")
        elif "edit_client" in request.POST:
            # Editing an existing client
            client_id = request.POST.get("client_id")
            client = get_object_or_404(Client, pk=client_id, company_owner=request.user)
            edit_form = ClientForm(request.POST, instance=client)
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, "Client updated successfully.")
                return redirect("profiles:client_management")
            edit_forms[client.id] = edit_form  # Update with validation errors if any
        elif "delete_client" in request.POST:
            # Deleting a client
            client_id = request.POST.get("client_id")
            client = get_object_or_404(Client, pk=client_id, company_owner=request.user)
            client.delete()
            messages.success(request, "Client deleted successfully.")
            return redirect("profiles:client_management")

    return render(
        request,
        "profiles/index.html",
        {"clients": clients, "add_form": add_form, "edit_forms": edit_forms},
    )
