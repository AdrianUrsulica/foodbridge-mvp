from django.urls import path
from . import views

urlpatterns = [
    path("", views.role_home, name="role_home"),
    path("register/", views.register_view, name="register"),
    path("donor/", views.donor_home, name="donor_home"),
    path("recipient/", views.recipient_home, name="recipient_home"),
]