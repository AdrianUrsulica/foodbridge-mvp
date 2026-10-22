
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.role_home, name="role_home"),

    path("register/", views.register_view, name="register"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("donor/", views.donor_home, name="donor_home"),

    path("recipient/", views.recipient_home, name="recipient_home"),
]
