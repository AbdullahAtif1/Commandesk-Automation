from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from .models import CustomUser


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

        # Save the updated user instance
        user.profile_needs_update = True
        user.save()
        

@receiver(pre_social_login)
def social_account_login(sender, request, sociallogin, **kwargs):
    """
    Ensure that the social account is linked to an existing user.
    If a user is already registered with the same email, link the accounts.
    """
    if sociallogin.is_existing:
        return
    
    user = sociallogin.user
    email = user.email
    
    try:
        existing_user = CustomUser.objects.get(email=email)
        sociallogin.user = existing_user
        sociallogin.save(request)
    except CustomUser.DoesNotExist:
        # The user is new, so continue with the regular signup flow
        pass

