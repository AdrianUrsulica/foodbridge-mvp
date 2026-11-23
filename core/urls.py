
from django.urls import path
from . import views

urlpatterns = [
    path("", views.food_listings, name="food_listings"),
    path("create/", views.create_food_listing, name="create_food_listing"),
    path("mine/", views.my_food_listings, name="my_food_listings"),
    path(
        "<int:pk>/edit/",
        views.edit_food_listing,
        name="edit_food_listing",
    ),
    path(
        "<int:pk>/delete/",
        views.delete_food_listing,
        name="delete_food_listing",
    ),
]

