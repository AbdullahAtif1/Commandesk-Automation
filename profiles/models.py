from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class CustomUser(AbstractUser): # Forgot to add the company_name field 🤦‍♂️
    profile_picture = models.ImageField(upload_to="imgs/profile_pictures/", blank=True, null=True, verbose_name=_("Profile Picture"))
    company_logo = models.ImageField(upload_to="imgs/company_logos/", blank=True, null=True, verbose_name=_("Company Logo"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))
    store_location = models.TextField(blank=True, null=True, verbose_name=_("Store Location"))
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_("Phone Number"))
    company_name = models.CharField(max_length=250, null=True, blank=True, verbose_name=_("Company Name"))
    email_password = models.CharField(max_length=250, null=True, blank=True, verbose_name=_("Email Password"), help_text=_("Password or app-specific password for the company email."))
    

    class Meta:
        verbose_name = _( "Owners")
        verbose_name_plural = _( "Owners")

    def __str__(self):
        return self.username

class Subscription(models.Model):
    PLAN_CHOICES = [
        ("basic", "Basic"),
        ("standard", "Standard"),
        ("premium", "Premium"),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="subscription")
    plan_name = models.CharField(max_length=50, choices=PLAN_CHOICES, verbose_name=_("Plan Name"))
    start_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Start Date"))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_("End Date"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _( "Subscription")
        verbose_name_plural = _( "Subscriptions")

    def __str__(self):
        return f"{self.user.username} - {self.plan_name}"


class Client(models.Model):
    company_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clients",
        verbose_name=_("Company Owner")
    )
    CLIENT_TYPE_CHOICES = [
				("first_time", "First Time"),
				("repeat", "Repeat"),
				("loyal", "Loyal"),
				("high_value", "High Value"),
		]
    client_type = models.CharField(
				max_length=20,
				choices=CLIENT_TYPE_CHOICES,
				default="first_time",
				verbose_name=_("Client Type"),
				help_text=_("Categorize the client based on their relationship with your business."),
		)
    name = models.CharField(max_length=255, verbose_name=_("Client Name"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email Address"))
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_("Phone Number"))
    address = models.TextField(blank=True, null=True, verbose_name=_("Address"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Additional Notes"))
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Total Spent")) # Need to update the sales odel to update this
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ["-created_at"]	

