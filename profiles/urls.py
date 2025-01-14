from django.urls import path, include
from . import views

app_name = 'profiles'

urlpatterns = [
    path('client_management', views.client_management, name="client_management"),
		path("update-profile/<str:username>/<int:user_id>/", views.update_profile, name="update_profile"),
    path("<str:username>/<int:user_id>/", views.profile_detail, name="profile_detail"),

		path("cstm_login_redirect/", views.cstm_login_redirect, name="cstm_login_redirect"),

		path("cstm-signup/", views.signup_view, name="cstm_signup"),
    path("cstm-login/", views.login_view, name="cstm_login"),
]
