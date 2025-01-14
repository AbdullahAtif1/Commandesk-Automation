from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login

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

def cstm_login_redirect(request):
    return redirect("profiles:profile_detail", username=request.user.username, user_id=request.user.id)


@login_required
def update_profile(request, username, user_id):
    """
    View to update the profile of the logged-in user.
    """
    # Ensure the logged-in user matches the user being updated
    user = get_object_or_404(CustomUser, username=username, id=user_id)

    if user != request.user:
        messages.error(request, "You are not authorized to edit this profile.")
        return redirect("profiles:profile_detail", username=username, user_id=user_id)

    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profiles:profile_detail", username=user.username, user_id=user.id)
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, "profiles/update_profile.html", {"form": form, "user": user})



@login_required
def profile_detail(request, username, user_id):
    """
    View to display the profile of a user based on username and user ID.
    """
    user = get_object_or_404(CustomUser, username=username, id=user_id)
    return render(request, "profiles/profile_detail.html", {"user": user})


def signup_view(request):
    
    form = CustomSignupForm()
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully. You can log in now.")
            return redirect("profiles:cstm_login")  # Redirect to the login page
    else:
        form = CustomSignupForm()
    return render(request, "registration/signup.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("profiles:profile_detail", username=user.username, user_id=user.id)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})

