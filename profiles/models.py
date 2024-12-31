from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from datetime import timedelta

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to="imgs/profile_pictures/", blank=True, null=True, verbose_name=_("Profile Picture"))
    company_logo = models.ImageField(upload_to="imgs/company_logos/", blank=True, null=True, verbose_name=_("Company Logo"))
    website = models.URLField(blank=True, null=True, verbose_name=_("Website"))
    store_location = models.TextField(blank=True, null=True, verbose_name=_("Store Location"))
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name=_("Phone Number"))

    class Meta:
        verbose_name = _( "User")
        verbose_name_plural = _( "Users")

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


@receiver(user_signed_up)
def populate_user_details_on_social_auth(sender, request, user, sociallogin=None, **kwargs):
    """
    Populate fields for new users signing up through social authentication.
    Fields like profile_picture, email, and username are populated if available.
    Company-related info is left for later.
    """
    if sociallogin:  # Check if the login is via a social provider
        user_data = sociallogin.account.extra_data
        
        # Set default values in case the social login doesn't provide some data
        default_profile_picture = 'imgs/default.jpg'  # Replace with your default image URL/path
        default_username = user.email.split('@')[0]  # Default username can be part of the email

        # Populate fields based on provider
        if sociallogin.account.provider == 'google':
            user.email = user_data.get('email', user.email)
            user.profile_picture = user_data.get('picture', default_profile_picture)
            user.username = user.username or user_data.get('name', default_username)

        elif sociallogin.account.provider == 'facebook':
            user.email = user_data.get('email', user.email)
            # Fallback if the 'picture' field is missing or incomplete
            user.profile_picture = user_data.get('picture', {}).get('data', {}).get('url', default_profile_picture)
            user.username = user.username or user_data.get('name', default_username)

        # Save the updated user instance
        user.save()

