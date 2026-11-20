
from django.urls import path
from . import views

urlpatterns = [
    path(
        "create/",
        views.create_food_listing,
        name="create_food_listing",
    ),
]
